import unittest

from dccautomation import compat


class BackendTests(unittest.TestCase):

    def test_uninitialized_socket_behavior(self):
        # Verify that errors are raised when recv on an unconnected REQ
        # or sending on an unbound REP,
        # and uninitialized sockets can be closed.
        s = compat.MQ.socket(compat.MQ.REQ)
        self.assertRaises(compat.MQ.errtype, s.recv)
        s.close()

        s = compat.MQ.socket(compat.MQ.REP)
        self.assertRaises(compat.MQ.errtype, s.send, b'1')
        s.close()

    def test_invalid_socket_type(self):
        self.assertRaises(ValueError, compat.MQ.socket, -18484)


class CalcBackendTests(unittest.TestCase):

    def test_unknown(self):
        self.assertRaises(ValueError, compat.calc_backend, 'WTF')

    def test_no_matching(self):
        self.assertRaises(ImportError, compat.calc_backend, '', [])
