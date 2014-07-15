"""
Defines compatibility members for Python 2.6, Python3, etc.,
along with various IPC backends.
"""
import os
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
    return ZmqBackend()

def _nano():
    import nanomsg
    import socket

    class NanomsgBackend(object):
        errtype = nanomsg.NanoMsgAPIError

        def socket(self, socktype):
            return nanomsg.Socket(socktype)

        def recv_noblock(self, socket):
            return socket.recv(flags=nanomsg.DONTWAIT)

        def __getattr__(self, item):
            return getattr(nanomsg, item)

        def exclusive_bind(self, endpoint):
            path = endpoint.split('://')[-1]
            ip, port = path.split(':')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((ip, int(port)))
            return s

    return NanomsgBackend()

_env = os.environ.get('DCCAUTO_BACKEND', '').lower()
if _env == 'zmq':
    MQ = _zmq()
elif _env == 'nano':
    MQ = _nano()
else:
    assert not _env, 'Unrecognized backend: %s' % _env
    try:
        MQ = _nano()
    except ImportError:
        try:
            MQ = _zmq()
        except ImportError:
            raise ImportError('pyzmq or nanomsg-python must be installed.')
