import unittest

from dccautomation import compat


class BackendTests(unittest.TestCase):

    def test_new_socket_behavior(self):
        s = compat.MQ.socket(compat.MQ.REQ)
        self.assertRaises(compat.MQ.errtype, s.recv)
        # self.assertRaises(compat.MQ.errtype, s.send, '1')
        s.close()


class CalcBackendTests(unittest.TestCase):

    def test_unknown(self):
        self.assertRaises(ValueError, compat.calc_backend, 'WTF')

    def test_no_matching(self):
        self.assertRaises(ImportError, compat.calc_backend, '', [])
