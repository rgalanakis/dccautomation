from .. import configs, _compat, utils, Client


class HandshakeTests(_compat.unittest.TestCase):

    def make_client(self):
        cfg = configs.CurrentPython()
        proc = utils.start_server_process(cfg)
        client = Client(proc)
        return client

    def test_handshake_allows_multiple_procs(self):
        clients = [self.make_client() for _ in range(2)]
        for client in clients:
            client.exec_('import os')
            self.assertEqual(
                client.eval_('os.getpid()'),
                client.serverproc.popen.pid,
                'Wrong process received eval, '
                'probably only one started and bound properly.')
