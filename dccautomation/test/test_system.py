"""
System-level tests.
"""
import os

from .. import configs, utils, Client
from .._compat import unittest


def make_client():
    cfg = configs.CurrentPython()
    proc = utils.start_server_process(cfg)
    client = Client(proc)
    return client


class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = make_client()

    def test_is_another_proc(self):
        self.client.exec_('import os')
        got = self.client.eval_('os.getpid()')
        self.assertNotEqual(got, os.getpid())

    def test_eval(self):
        got = self.client.eval_('1 + 1')
        self.assertEqual(got, 2)

    def test_exec(self):
        self.client.exec_('a = 2 + 1')
        got = self.client.eval_('a')
        self.assertEqual(got, 3)

    def test_errortype_propagates(self):
        with self.assertRaises(TypeError):
            self.client.exec_('1 + ""')


class HandshakeTests(unittest.TestCase):
    def test_handshake_allows_multiple_procs(self):
        clients = [make_client() for _ in range(2)]
        for client in clients:
            client.exec_('import os')
            self.assertEqual(
                client.eval_('os.getpid()'),
                client.serverproc.popen.pid,
                'Wrong process received eval, '
                'probably only one started and bound properly.')
