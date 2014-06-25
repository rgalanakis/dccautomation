import mock
import os

from . import test_system
from .. import client, common, configs, server, utils


@mock.patch('os.environ', {})
class StartServerWithHandshakeTests(test_system.SystemTests):

    @classmethod
    def setUpClass(cls):
        cfg = configs.CurrentPython()
        with utils.Handshaker(cfg, os.environ) as handshake:
            server.start_server_thread()
        cls.client = client.Client(
            utils.ServerProc(None, handshake.app_endpoint, cfg))


@mock.patch('os.environ', {})
class StartServerNoHandshakeTests(test_system.SystemTests):
    @classmethod
    def setUpClass(cls):
        cfg = configs.CurrentPython()
        ep = 'tcp://127.0.0.1:9091'
        os.environ[common.ENV_CONFIGNAME] = cfg.cfgname()
        os.environ[common.ENV_APP_ENDPOINT] = ep
        server.start_server_thread()
        cls.client = client.Client(utils.ServerProc(None, ep, cfg))