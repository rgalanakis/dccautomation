import atexit
import os
import subprocess
import zmq


ENV_CONFIGNAME = 'DCCAUTO_CONFIGNAME'
ENV_HANDSHAKE = 'DCCAUTO_HANDSHAKE'


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


def start_server_process(config):
    handshake_info = create_rep_socket_bound_to_random()

    env = dict(os.environ)
    pythonpath = env.get('PYTHONPATH', '')
    env['PYTHONPATH'] = '{}{sep}{}{sep}{}'.format(
        pythonpath,
        _one_up_dir(__file__),
        _one_up_dir(zmq.__file__),
        sep=os.path.pathsep)
    env[ENV_HANDSHAKE] = handshake_info.endpoint
    env[ENV_CONFIGNAME] = config.cfgname()

    proc = subprocess.Popen(config.popen_args(), env=env)
    atexit.register(proc.kill)
    app_endpoint = handshake_info.socket.recv()
    handshake_info.socket.send('')
    handshake_info.socket.close()
    return ServerProc(proc, app_endpoint, config)
