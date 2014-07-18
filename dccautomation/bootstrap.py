"""
Code having to do with how the client boostraps the server,
such as process startup and handshaking.
"""

import atexit
import os
import subprocess

from . import common, compat, utils


def _one_up_dir(f):
    return os.path.dirname(os.path.dirname(f))


class ServerProc(object):
    """
    Information about a server process.

    :param popen: The ``subprocess.Popen`` instance representing the server
      process. Can usually be None if you didn't start the process.
    :type popen: subprocess.Popen | None
    :param endpoint: Endpoint string pointing to the server process.
    :param config: Configuration the server was started with.
    :type config: dccautomation.configs.Confg
    """
    def __init__(self, popen, endpoint, config):
        self.popen = popen
        self.endpoint = endpoint
        self.config = config


class Handshaker(object):
    """
    Context manager which encapsulates the
    client and server handshake mechanism,
    used to have the server bind to a unique port.
    This class should only be used by the client.

    On enter, a port will be bound to (the handshake port),
    and items in ``environ`` are set so the server knows what the handshake
    port is.

    Under the context manager, the client should start the server,
    usually using :func:`start_server_process`.
    The server startup (see :func:`dccautomation.server.start_server`)
    will send the environment variables to the server process.
    On startup, the server will bind to its own port (the application port),
    send that port number to the client, and wait for an acknowledgement.

    On exit, the client will wait to hear the application port,
    send an acknowledgement, and then close the handshake port.

    :param config: dccautomation.configs.Config
    :param environ: Environment variable dictionary.
      Will be modified during handshake.
    """
    def __init__(self, config, environ):
        self._config = config
        self._environ = environ
        self._handshake_info = None
        self.app_endpoint = None

    def __enter__(self):
        self._handshake_info = utils.create_rep_socket_bound_to_random()
        self._environ[common.ENV_HANDSHAKE_ENDPOINT] = (
            self._handshake_info.endpoint)
        self._environ[common.ENV_CONFIGNAME] = self._config.cfgname()
        return self

    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self.app_endpoint = self._config.loads(
                self._handshake_info.socket.recv())
            self._handshake_info.socket.send(b'ack')
            self._handshake_info.socket.close()


def start_server_process(config):
    """
    Starts a new server process using the given config.
    Provides handshake environment variables for the new environment,
    and sets up paths.

    :type config: dccautomation.configs.Config
    """
    env = dict(os.environ)
    with Handshaker(config, env) as handshake:
        proc = start_process(config.popen_args(), env)
        atexit.register(proc.kill)
    return ServerProc(proc, handshake.app_endpoint, config)


def start_process(args, env=None, **kwargs):
    """
    Starts a new process.
    The PYTHONPATH is set in the new process to be able to run
    ``dccautomation`` code.
    """
    if env is None:
        env = dict(os.environ)
    pythonpath = [env.get('PYTHONPATH', ''), _one_up_dir(__file__)]
    mqfilename = getattr(compat.MQ, '__file__', None)
    if mqfilename:
        pythonpath.append(mqfilename)
    env['PYTHONPATH'] = os.path.pathsep.join(pythonpath)
    proc = subprocess.Popen(args, env=env, **kwargs)
    return proc
