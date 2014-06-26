import os

from . import bootstrap, client, common, server


DEFAULT_INPROC_PORT = 9091


def get_default_port():
    return int(os.getenv(common.ENV_INPROC_PORT, DEFAULT_INPROC_PORT))


def start_inproc_client(config, port=None):
    endpoint = 'tcp://127.0.0.1:%s' % (port or get_default_port())
    c = client.Client(bootstrap.ServerProc(None, endpoint, config))
    return c


def start_inproc_server(config, port=None):
    os.environ[common.ENV_CONFIGNAME] = config.cfgname()
    os.environ[common.ENV_APP_ENDPOINT] = 'tcp://127.0.0.1:%s' % (
        port or get_default_port())
    server.start_server_thread()
