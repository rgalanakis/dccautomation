import logging
import zmq


def is_open(endpoint):
    """
    Return True if ``endpoint`` can be bound to.
    """
    try:
        sock = zmq.Context().socket(zmq.REP)
        sock.bind(endpoint)
        sock.close()
        return True
    except zmq.ZMQError:
        return False


class SocketConn(object):
    """Information about a bound/connected socket
    (the socket instance, the host, and port).
    """
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
    """
    Return a logger using an easy-to-understand name that includes
    the endpoint.
    """
    simple_endpoint = endpoint.split('://')[-1]
    host, port = simple_endpoint.split(':')
    if host in ('127.0.0.1', 'localhost'):
        host = 'lo'
    else:
        host = host.replace('.', '_')
    fullname = '%s.%s-%s' % (name, host, port)
    return logging.getLogger(fullname)
