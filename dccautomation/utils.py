import atexit
import contextlib
import os
import subprocess
import zmq

from . import common


class SocketConn(object):
    def __init__(self, socket, host, port):
        self.socket = socket
        self.host = host
        self.port = port
        self.endpoint = '%s:%s' % (host, port)


def create_rep_socket_bound_to_random():
    sock = zmq.Context().socket(zmq.REP)
    host = 'tcp://127.0.0.1'
    port = sock.bind_to_random_port(host)
    return SocketConn(sock, host, port)


def _one_up_dir(f):
    return os.path.dirname(os.path.dirname(f))


class ServerProc(object):

    def __init__(self, popen, endpoint, config):
        self.popen = popen
        self.endpoint = endpoint
        self.config = config


class Handshaker(object):
    def __init__(self, config, environ):
        self._config = config
        self._environ = environ
        self._handshake_info = None
        self.app_endpoint = None

    def __enter__(self):
        self._handshake_info = create_rep_socket_bound_to_random()
        self._environ[common.ENV_HANDSHAKE] = self._handshake_info.endpoint
        self._environ[common.ENV_CONFIGNAME] = self._config.cfgname()
        return self

    def __exit__(self, *_):
        self.app_endpoint = self._handshake_info.socket.recv()
        self._handshake_info.socket.send('')
        self._handshake_info.socket.close()


def start_server_process(config):
    env = dict(os.environ)
    with Handshaker(config, env) as handshake:
        pythonpath = env.get('PYTHONPATH', '')
        env['PYTHONPATH'] = '{}{sep}{}{sep}{}'.format(
            pythonpath,
            _one_up_dir(__file__),
            _one_up_dir(zmq.__file__),
            sep=os.path.pathsep)
        proc = subprocess.Popen(config.popen_args(), env=env)
        atexit.register(proc.kill)
    return ServerProc(proc, handshake.app_endpoint, config)
