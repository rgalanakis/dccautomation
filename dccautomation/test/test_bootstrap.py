import os

from .. import _compat, bootstrap, client, configs
from . import systemtest_mixins


def make_client():
    cfg = configs.CurrentPython()
    proc = bootstrap.start_server_process(cfg)
    c = client.Client(proc)
    return c


class IpcSystemTests(systemtest_mixins.SystemTests, _compat.unittest.TestCase):

    @classmethod
    def new_client(cls):
        return make_client()

    def test_is_in_different_proc(self):
        self.client.exec_('import os')
        pid = int(self.client.eval_('os.getpid()'))
        self.assertNotEqual(pid, os.getpid())


class HandshakeTests(_compat.unittest.TestCase):
    def setUp(self):
        self.clients = [make_client() for _ in range(2)]

    def test_handshake_supports_multiple_procs(self):
        for c in self.clients:
            c.exec_('import os')
            self.assertEqual(
                c.eval_('os.getpid()'),
                c.serverproc.popen.pid,
                'Wrong process received eval, '
                'probably only one started and bound properly.')


class HandshakerTests(_compat.unittest.TestCase):

    def test_does_not_handshake_if_error_occurred(self):
        with self.assertRaises(ZeroDivisionError):
            with bootstrap.Handshaker(configs.CurrentPython(), {}) as h:
                _ = 1 / 0
        self.assertIsNone(h.app_endpoint)
