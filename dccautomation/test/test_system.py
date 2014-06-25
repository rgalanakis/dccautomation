"""
System-level tests.
"""
import os

from .. import client, configs, utils
from .._compat import unittest


def make_client():
    cfg = configs.CurrentPython()
    proc = utils.start_server_process(cfg)
    c = client.Client(proc)
    return c


class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = make_client()

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

    def test_timeout(self):
        self.client.timeout_secs = 0.0
        with self.assertRaises(client.Timeout):
            self.client.exec_('import time; time.sleep(0.1')

    def test_invalid_method(self):
        with self.assertRaises(client.InvalidMethod):
            self.client.sendrecv(['abc', 1])


class HandshakeTests(unittest.TestCase):
    def test_handshake_allows_multiple_procs(self):
        clients = [make_client() for _ in range(2)]
        for c in clients:
            c.exec_('import os')
            self.assertEqual(
                c.eval_('os.getpid()'),
                c.serverproc.popen.pid,
                'Wrong process received eval, '
                'probably only one started and bound properly.')
            self.assertNotEqual(
                c.eval_('os.getpid()'),
                os.getpid(),
                'Evalled in this process, not sure why.')
