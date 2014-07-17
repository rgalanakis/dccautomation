import unittest

from dccautomation import compat


class BackendTests(unittest.TestCase):

    def test_new_socket_behavior(self):
        s = compat.MQ.socket(compat.MQ.REQ)
        self.assertRaises(compat.MQ.errtype, s.recv)
        # self.assertRaises(compat.MQ.errtype, s.send, '1')
        s.close()


class FifoTests(unittest.TestCase):
    def setUp(self):
        self.MQ = compat._fifo()

    def test_stomp_rep(self):
        self.MQ.stomp_binds = True
        s1 = self.MQ.socket(self.MQ.REP)
        s1.bind('tcp://127.0.0.1:610003')
        s2 = self.MQ.socket(self.MQ.STOMP_REP)
        s2.bind('tcp://127.0.0.1:610003')

    def test_socket_type(self):
        self.assertRaises(ValueError, self.MQ.socket, 'HI')


class CalcBackendTests(unittest.TestCase):

    def test_unknown(self):
        self.assertRaises(ValueError, compat.calc_backend, 'WTF')

    def test_no_matching(self):
        self.assertRaises(ImportError, compat.calc_backend, '', [])
