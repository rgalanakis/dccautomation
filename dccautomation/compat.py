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

    range = range


def safe_mkfifo(path):
    try:
        os.mkfifo(path)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


def safe_unlink(path):
    try:
        os.unlink(path)
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise

def _zmq():
    import zmq

    class ZmqBackend(object):
        errtype = zmq.ZMQError

        def socket(self, socktype):
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
            return nanomsg.Socket(socktype)

        def recv_noblock(self, socket_):
            return socket_.recv(flags=nanomsg.DONTWAIT)

        def __getattr__(self, item):
            return getattr(nanomsg, item)

        def exclusive_bind(self, endpoint):
            # nanomq will re-use its endpoint in the same process,
            # so we need to use Python's socket module.
            path = endpoint.split('://')[-1]
            ip, port = path.split(':')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((ip, int(port)))
            return s

        def closes_reliably(self):
            # See https://github.com/rgalanakis/dccautomation/issues/1
            return False

    return NanomsgBackend()

def _fifo():
    import fcntl

    class FifoError(Exception):
        pass

    class FifoApiError(FifoError):
        def __init__(self, errno):
            self.errno = errno
            FifoError.__init__(self, str(errno))

    # noinspection PyAttributeOutsideInit
    class FifoSocket(object):
        def __init__(self, socket_type):
            self.socket_type = socket_type
            self.port = None
            self._did_recv = False
            self._setup = False

        def set_paths(self, endpoint):
            path = endpoint.split('://')[-1]
            host, port = path.split(':')
            self.port = port
            self.reqpath = '/tmp/%s.%s.req.fifo' % (host, port)
            self.reppath = '/tmp/%s.%s.rep.fifo' % (host, port)
            reqlock = '/tmp/%s.%s.req.lock' % (host, port)
            replock = '/tmp/%s.%s.rep.lock' % (host, port)
            self.lockpaths = reqlock, replock
            if self.socket_type == FifoBackend.REQ:
                self.sendpath = self.reqpath
                self.recvpath = self.reppath
                self.lockpath = reqlock
            else:
                self.sendpath = self.reppath
                self.recvpath = self.reqpath
                self.lockpath = replock

        def bind(self, endpoint):
            self.set_paths(endpoint)
            safe_mkfifo(self.sendpath)
            safe_mkfifo(self.recvpath)
            if os.path.exists(self.lockpath):
                raise FifoApiError(FifoBackend.EADDRINUSE)
            safe_mkfifo(self.lockpath)
            self._setup = True

        def connect(self, endpoint):
            self.set_paths(endpoint)
            safe_mkfifo(self.sendpath)
            safe_mkfifo(self.recvpath)
            safe_mkfifo(self.lockpath)
            self._setup = True

        def send(self, data):
            if not self._setup:
                raise FifoError('Must call bind or connect first.')
            fd = os.open(self.sendpath, os.O_WRONLY)
            # _, writes, _ = select.select([], [fd], [])
            # assert len(writes) == 1
            # assert writes[0] is fd
            os.write(fd, data)
            os.close(fd)

        def recv(self, block=True):
            if not self._setup:
                raise FifoError('Must call bind or connect first.')
            if block:
                fd = os.open(self.recvpath, os.O_RDONLY)
                reads, _, _ = select.select([fd], [], [])
            else:
                fd = os.open(self.recvpath, os.O_RDONLY | os.O_NONBLOCK)
                reads, _, _ = select.select([fd], [], [], 0)
                if not reads:
                    raise FifoApiError(FifoBackend.EAGAIN)
            assert len(reads) == 1
            assert reads[0] is fd
            f = os.fdopen(fd)
            try:
                read = f.read()
            except IOError as ex:
                if ex.errno == errno.EWOULDBLOCK:
                    raise FifoApiError(FifoBackend.EAGAIN)
                raise
            finally:
                f.close()
            if read == '':
                raise FifoApiError(FifoBackend.EAGAIN)
            return read

        def close(self):
            if self._setup:
                os.unlink(self.lockpath)
                if not any(os.path.exists(p) for p in self.lockpaths):
                    safe_unlink(self.sendpath)
                    safe_unlink(self.recvpath)
            self._setup = False

        def __del__(self):
            self.close()

        def __str__(self):
            return 'FifoSock(%s, %s)' % (self.port, self.socket_type)

        __repr__ = __str__

    class FifoBackend(object):
        REQ = 'REQ'
        REP = 'REP'
        EADDRINUSE = errno.EEXIST
        EAGAIN = -123
        errtype = FifoError
        __file__ = sys.executable

        def socket(self, socktype):
            return FifoSocket(socktype)

        def recv_noblock(self, socket_):
            return socket_.recv(False)

        def exclusive_bind(self, endpoint):
            s = self.socket(self.REP)
            s.bind(endpoint)
            return s

        def closes_reliably(self):
            return True

    return FifoBackend()

MQ = _fifo()
# _env = os.environ.get('DCCAUTO_BACKEND', '').lower()
# if _env == 'zmq':
#     MQ = _zmq()
# elif _env == 'nano':
#     MQ = _nano()
# else:
#     assert not _env, 'Unrecognized backend: %s' % _env
#     try:
#         MQ = _nano()
#     except ImportError:
#         try:
#             MQ = _zmq()
#         except ImportError:
#             raise ImportError('pyzmq or nanomsg-python must be installed.')
