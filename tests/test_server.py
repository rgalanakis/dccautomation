import os

import mock

from dccautomation import (
    compat, bootstrap, client, common, configs, inproc, server, utils)
from . import systemtest_mixins


@mock.patch('os.environ', {})
class StartServerWithHandshakeTests(systemtest_mixins.SystemTests,
                                    compat.unittest.TestCase):

    @classmethod
    def new_client(cls):
        cfg = configs.CurrentPython()
        with bootstrap.Handshaker(cfg, os.environ) as handshake:
            server.start_server_thread()
        return client.Client(
            bootstrap.ServerProc(None, handshake.app_endpoint, cfg))

    def test_eval_and_exec_do_not_modify_global_state(self):
        func = server.start_server
        for method in [self.client.eval_, self.client.exec_]:
            with self.assertRaises(NameError):
                # eval/exec should not have access to this function.
                method('%s.__name__' % func.__name__)


@mock.patch('os.environ', {})
class StartServerNoHandshakeTests(systemtest_mixins.SystemTests,
                                  compat.unittest.TestCase):
    # We need to make sure each call to new_client doesn't use the same
    # address as a previous call, so increment.
    _port_counter = 1025

    @classmethod
    def new_client(cls):
        cls._port_counter += 1
        cfg = configs.CurrentPython()
        for _ in compat.range(100):
            cl = inproc.start_inproc_client(cfg, cls._port_counter)
            if utils.is_open(cl.serverproc.endpoint):
                inproc.start_inproc_server(cfg, cls._port_counter)
                break
            cl.socket.close()
        else:
            raise AssertionError('Could not find an open port.')
        return cl


@mock.patch('os.environ', {})
class StartServerFatalErrorTests(compat.unittest.TestCase):

    def test_no_config_name(self):
        with self.assertRaises(SystemExit):
            server.start_server()

    def test_no_endpoint(self):
        os.environ[common.ENV_CONFIGNAME] = configs.CurrentPython().cfgname()
        with self.assertRaises(SystemExit):
            server.start_server()
