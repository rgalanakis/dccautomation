"""
System-level tests.
"""
import os

from .. import _compat, client, configs, utils
from . import systemtest_mixins


def make_client():
    cfg = configs.CurrentPython()
    proc = utils.start_server_process(cfg)
    c = client.Client(proc)
    return c


class SystemTests(_compat.unittest.TestCase, systemtest_mixins.SystemTests):
    @classmethod
    def setUpClass(cls):
        cls.client = make_client()


class HandshakeTests(_compat.unittest.TestCase):
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
