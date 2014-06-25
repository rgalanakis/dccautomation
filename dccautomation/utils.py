import logging
import zmq


def is_open(endpoint):
    try:
        sock = zmq.Context().socket(zmq.REP)
        sock.bind(endpoint)
        sock.close()
        return True
    except zmq.ZMQError:
        return False


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


def logger(name, endpoint):
    simple_endpoint = endpoint.split('://')[-1]
    host, port = simple_endpoint.split(':')
    if host in ('127.0.0.1', 'localhost'):
        host = 'lo'
    else:
        host = host.replace('.', '_')
    fullname = '%s.%s-%s' % (name, host, port)
    return logging.getLogger(fullname)
