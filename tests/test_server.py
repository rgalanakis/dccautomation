import os

import mock

from .. import (
    _compat, bootstrap, client, common, configs, inproc, server, utils)
from test import systemtest_mixins


@mock.patch('os.environ', {})
class StartServerWithHandshakeTests(systemtest_mixins.SystemTests,
                                    _compat.unittest.TestCase):

    @classmethod
    def new_client(cls):
        cfg = configs.CurrentPython()
        with bootstrap.Handshaker(cfg, os.environ) as handshake:
            server.start_server_thread()
        return client.Client(
            bootstrap.ServerProc(None, handshake.app_endpoint, cfg))


@mock.patch('os.environ', {})
class StartServerNoHandshakeTests(systemtest_mixins.SystemTests,
                                  _compat.unittest.TestCase):
    # We need to make sure each call to new_client doesn't use the same
    # address as a previous call, so increment.
    _port_counter = 1025

    @classmethod
    def new_client(cls):
        cls._port_counter += 1
        cfg = configs.CurrentPython()
        cl = inproc.start_inproc_client(cfg, cls._port_counter)
        assert utils.is_open(cl.serverproc.endpoint)
        inproc.start_inproc_server(cfg, cls._port_counter)
        return cl


@mock.patch('os.environ', {})
class StartServerFatalErrorTests(_compat.unittest.TestCase):

    def test_no_config_name(self):
        with self.assertRaises(SystemExit):
            server.start_server()

    def test_no_endpoint(self):
        os.environ[common.ENV_CONFIGNAME] = configs.CurrentPython().cfgname()
        with self.assertRaises(SystemExit):
            server.start_server()
