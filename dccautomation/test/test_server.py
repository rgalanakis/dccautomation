import mock
import os

from . import systemtest_mixins
from .. import _compat, bootstrap, client, common, configs, server


@mock.patch('os.environ', {})
class StartServerWithHandshakeTests(systemtest_mixins.SystemTests,
                                    _compat.unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cfg = configs.CurrentPython()
        with bootstrap.Handshaker(cfg, os.environ) as handshake:
            server.start_server_thread()
        cls.client = client.Client(
            bootstrap.ServerProc(None, handshake.app_endpoint, cfg))


@mock.patch('os.environ', {})
class StartServerNoHandshakeTests(systemtest_mixins.SystemTests,
                                  _compat.unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg = configs.CurrentPython()
        ep = 'tcp://127.0.0.1:9091'
        os.environ[common.ENV_CONFIGNAME] = cfg.cfgname()
        os.environ[common.ENV_APP_ENDPOINT] = ep
        server.start_server_thread()
        cls.client = client.Client(bootstrap.ServerProc(None, ep, cfg))


@mock.patch('os.environ', {})
class StartServerFatalErrorTests(_compat.unittest.TestCase):

    def test_no_config_name(self):
        with self.assertRaises(SystemExit):
            server.start_server()

    def test_no_endpoint(self):
        os.environ[common.ENV_CONFIGNAME] = configs.CurrentPython().cfgname()
        with self.assertRaises(SystemExit):
            server.start_server()
