from .. import configs, _compat, Client


class HandshakeTests(_compat.unittest.TestCase):

    def make_all(self):
        cfg = configs.HandshakingConfig(configs.CurrentPython)
        proc = configs.start_server_process(cfg)
        client = Client(cfg)
        return cfg, proc, client

    def test_handshake_allows_multiple_procs(self):
        cfg1, proc1, client1 = self.make_all()
        cfg2, proc2, client2 = self.make_all()
        for proc, client in [(proc1, client1), (proc2, client2)]:
            client.exec_('import os')
            self.assertEqual(
                client.eval_('os.getpid()'),
                proc.pid,
                'Wrong process received eval, '
                'probably only one started and bound properly.')
