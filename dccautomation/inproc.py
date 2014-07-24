import os

from . import bootstrap, client, common, server


DEFAULT_INPROC_PORT = 9091


def get_default_port():
    return int(os.getenv(common.ENV_INPROC_PORT, DEFAULT_INPROC_PORT))


def start_inproc_client(config, port=None):
    endpoint = 'tcp://127.0.0.1:%s' % (port or get_default_port())
    c = client.Client(bootstrap.ServerProc(None, endpoint, config))
    return c


def start_inproc_server(config_or_env, port=None):
    if port is None:
        port = get_default_port()
    env = config_or_env
    if hasattr(config_or_env, 'cfgname'):
        env = dict(os.environ)
        env[common.ENV_CONFIGNAME] = config_or_env.cfgname()
        env[common.ENV_APP_ENDPOINT] = 'tcp://127.0.0.1:%s' % port
    server.start_server_thread(env)
