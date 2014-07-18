"""
Defines compatibility members for Python 2.6, Python3, etc.,
along with various IPC backends.
"""
import errno
import os
import select
import sys

try:
    # noinspection PyPackageRequirements
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest

if sys.version_info[0] == 2:
    # noinspection PyUnresolvedReferences
    import __builtin__ as builtins

    # noinspection PyShadowingBuiltins
    reload = reload

    # noinspection PyShadowingBuiltins
    def exec_(s, globals=None, locals=None):
        # noinspection PyRedundantParentheses
        exec (s) in globals, locals

    # noinspection PyShadowingBuiltins
    range = xrange
else:
    # noinspection PyUnresolvedReferences
    import builtins

    import imp as _imp
    # noinspection PyShadowingBuiltins
    reload = _imp.reload

    # noinspection PyShadowingBuiltins
    def exec_(s, globals=None, locals=None):
        exec (s, globals, locals)

    # noinspection PyShadowingBuiltins
    range = range


def safe_mkfifo(path):
    """os.mkfifo but do not raise if file exists."""
    try:
        os.mkfifo(path)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


def safe_unlink(path):
    """os.unlink but do not raise if file exists."""
    try:
        os.unlink(path)
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise


def endpoint_to_addr(endpoint):
    path = endpoint.split('://')[-1]
    host, port = path.split(':')
    return host, int(port)


def _check_socket_type(backend, se):
    if se not in (backend.REQ, backend.REP):
        raise ValueError('Invalid socket type: %r' % se)


def _zmq():
    import zmq

    class ZmqBackend(object):
        errtype = zmq.ZMQError

        def socket(self, socktype):
            _check_socket_type(self, socktype)
            return zmq.Context().socket(socktype)

        def recv_noblock(self, socket):
            return socket.recv(zmq.NOBLOCK)

        def __getattr__(self, item):
            return getattr(zmq, item)

        def exclusive_bind(self, endpoint):
            sock = self.socket(self.REP)
            sock.bind(endpoint)
            return sock

        def closes_reliably(self):
            return True

    return ZmqBackend()

def _nano():
    import nanomsg
    import socket

    class NanomsgBackend(object):
        errtype = nanomsg.NanoMsgAPIError

        def socket(self, socktype):
            _check_socket_type(self, socktype)
            return nanomsg.Socket(socktype)

        def recv_noblock(self, socket_):
            return socket_.recv(flags=nanomsg.DONTWAIT)

        def __getattr__(self, item):
            return getattr(nanomsg, item)

        def exclusive_bind(self, endpoint):
            # nanomq will re-use its endpoint in the same process,
            # so we need to use Python's socket module.
            addr = endpoint_to_addr(endpoint)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(addr)
            return s

        def closes_reliably(self):
            # See https://github.com/rgalanakis/dccautomation/issues/1
            return False

    return NanomsgBackend()

def _fifo():
    import glob
    REQ = 'REQ'
    REP = 'REP'
    EADDRINUSE = errno.EEXIST
    EAGAIN = -123

    def errorcode(errno_):
        if errno_ == EAGAIN:
            return 'EAGAIN'
        return errno.errorcode[errno_]

    def pid_exists(pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    def touch(path):
        with open(path, 'w'):
            return path

    class FifoError(Exception):
        pass

    class FifoApiError(FifoError):
        def __init__(self, errno_):
            self.errno = errno_
            FifoError.__init__(self, errno_, errorcode(errno_))

    class FifoBackend(object):

        def __init__(self):
            self.errtype = FifoError
            self.REQ = REQ
            self.REP = REP
            self.EAGAIN = EAGAIN
            self.EADDRINUSE = EADDRINUSE

        def socket(self, socket_type):
            _check_socket_type(self, socket_type)
            return FifoSocket(socket_type)

        def recv_noblock(self, socket_):
            return socket_.recv(False)

        def exclusive_bind(self, endpoint):
            s = self.socket(REP)
            s.bind(endpoint)
            return s

        def closes_reliably(self):
            return True

    # noinspection PyTypeChecker
    class FifoSocket(object):
        """
        Object that emulates a zmq/nanomsg socket using FIFO on linux/OSX.
        A pair of files are created (req/rep) and client/server
        reads and writes to those files.
        Some other files are created for bookkeeping purposes.
        There are definitely some edge cases and race conditions here,
        but it should be good enough as a fallback.
        """
        LOCK = 'lock'
        FIFO = 'fifo'

        def __init__(self, socket_type):
            self.socket_type = socket_type
            self.other_socket_type = REQ if socket_type == REP else REP
            self.host = None
            self.port = None
            self.sendpath = None
            self.recvpath = None
            self.lockpaths = None
            self.lockpath = None
            self.bindlockpath = None
            self._bound_or_connected = False
            self._closed = False

        def _getpath(self, *parts):
            assert parts
            result = '/tmp/dccauto.%s.%s.' % (self.host, self.port)
            result += '.'.join([str(p) for p in parts])
            return result

        def _get_tofrom_paths(self, pathtype):
            def path(s):
                return self._getpath(s, pathtype)
            return path(self.socket_type), path(self.other_socket_type)

        def set_paths(self, endpoint):
            self.host, self.port = endpoint_to_addr(endpoint)
            self.sendpath, self.recvpath = self._get_tofrom_paths(self.FIFO)
            self.lockpaths = self._get_tofrom_paths(self.LOCK)
            self.lockpath = self.lockpaths[0]
            safe_mkfifo(self.sendpath)
            safe_mkfifo(self.recvpath)

        def bind(self, endpoint):
            """
            Bind to an endpoint.

            When we bind, we make the normal fifo and lock files,
            but we also make a 'bindlock' file with the current process' pid.
            Before binding, we check if a bindlock exists for the given
            address. If it does, and the pid of the bindlock file is running,
            we assume the address is in use, and raise an error.
            If the pid is not running, we delete it. It was probably left
            over after the process died and didn't clean it up.
            """
            self.set_paths(endpoint)
            if os.path.isfile(self.lockpath):
                path = self._getpath('bindlock')
                for existing_bindlock in glob.iglob(path + '.*'):
                    pid = int(existing_bindlock.rsplit('.', 1)[-1])
                    if pid_exists(pid):
                        raise FifoApiError(EADDRINUSE)
                    else:
                        safe_unlink(existing_bindlock)
            self.bindlockpath = touch(self._getpath('bindlock', os.getpid()))
            touch(self.lockpath)
            self._bound_or_connected = True

        def connect(self, endpoint):
            self.set_paths(endpoint)
            touch(self.lockpath)
            self._bound_or_connected = True

        def _check_state(self):
            if self._closed or not self._bound_or_connected:
                raise FifoError('Socket in invalid state.')

        def send(self, data):
            self._check_state()
            fd = os.open(self.sendpath, os.O_WRONLY)
            try:
                os.write(fd, data)
            finally:
                os.close(fd)

        def recv(self, blocking=True):
            self._check_state()
            flags = os.O_RDONLY
            args = [[], []]
            if not blocking:
                flags |= os.O_NONBLOCK
                args.append(0)
            fd = os.open(self.recvpath, flags)
            reads, _, _ = select.select([fd], *args)
            if not blocking and not reads:
                raise FifoApiError(EAGAIN)
            assert len(reads) == 1
            assert reads[0] is fd
            fileobj = os.fdopen(fd)
            try:
                data = fileobj.read()
            except IOError as ex:
                if ex.errno == errno.EWOULDBLOCK:
                    raise FifoApiError(EAGAIN)
                raise
            finally:
                fileobj.close()
            if not data:
                raise FifoApiError(EAGAIN)
            return data.encode('utf-8')

        def close(self):
            if self._closed:
                return
            if not self._bound_or_connected:
                return
            safe_unlink(self.lockpath)
            if self.bindlockpath:
                safe_unlink(self.bindlockpath)
            if not any(os.path.exists(p) for p in self.lockpaths):
                safe_unlink(self.sendpath)
                safe_unlink(self.recvpath)
            self._closed = True

        def __del__(self):
            self.close()

        def __str__(self):
            return 'FifoSock(%s, %s)' % (self.port, self.socket_type)

        __repr__ = __str__

    return FifoBackend()


BACKENDS = ('zmq', 'nano', 'fifo')

def calc_backend(backend, backends=BACKENDS):
    backend = backend.lower()
    if backend in backends:
        # noinspection PyCallingNonCallable
        return globals()['_' + backend]()
    if backend:
        raise ValueError('Unrecognized backend: %s' % backend)
    funcs = [globals()['_' + name] for name in backends]
    for func in funcs:
        try:
            return func()
        except ImportError:
            pass
    msg = (
        'No valid backend could be created. '
        'pyzmq or nanomsg-python must be installed, '
        'or you must use a Linux-based system for FIFO support.')
    raise ImportError(msg)

MQ = calc_backend(os.environ.get('DCCAUTO_BACKEND', ''))
