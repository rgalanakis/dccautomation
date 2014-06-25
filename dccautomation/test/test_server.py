import os

from . import test_system
from .. import _compat, client, common, configs, server, utils


class StartServerTests(test_system.SystemTests):

    @classmethod
    def setUpClass(cls):
        cfg = configs.CurrentPython()
        with utils.Handshaker(cfg, os.environ) as handshake:
            server.start_server_thread()
        cls.client = client.Client(
            utils.ServerProc(None, handshake.app_endpoint, cfg))
