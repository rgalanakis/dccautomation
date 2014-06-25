import os
import zmq

from .. import _compat, client, common, configs, server, utils


class StartServerTests(_compat.unittest.TestCase):

    def test_handshake(self):
        cfg = configs.CurrentPython()
        with utils.Handshaker(cfg, os.environ) as handshake:
            server.start_server_thread()
        c = client.Client(utils.ServerProc(None, handshake.app_endpoint, cfg))
        got = c.eval_('1 + 1')
        self.assertEqual(got, 2)
