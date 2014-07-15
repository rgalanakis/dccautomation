import logging
import random

from . import compat

EPHEMERAL_PORT_RANGE = 49152, 61000

def is_open(endpoint):
    """
    Return True if ``endpoint`` can be bound to.
    """
    try:
        sock = compat.MQ.exclusive_bind(endpoint)
        sock.close()
        return True
    except Exception as ex:
        if getattr(ex, 'errno', None) == compat.MQ.EADDRINUSE:
            return False
        raise


def assert_open(arg, state=True):
    endpoint = getattr(arg, 'endpoint', arg)
    assert is_open(endpoint) == state, (
        'is_open(%s) should be %s' % (endpoint, state))


class SocketConn(object):
    """Information about a bound/connected socket
    (the socket instance, the host, and port).
    """
    def __init__(self, socket, host, port):
        self.socket = socket
        self.host = host
        self.port = port
        self.endpoint = '%s:%s' % (host, port)

# Copied from ZMQ src
def _bind_to_random_port(
        socket, addr, min_port=49152, max_port=65536, max_tries=10000):
    for _ in compat.range(max_tries):
        try:
            port = random.randrange(min_port, max_port)
            socket.bind('%s:%s' % (addr, port))
            return port
        except compat.MQ.errtype as ex:
            if ex.errno != compat.MQ.EADDRINUSE:
                raise
    raise RuntimeError('Could not bind socket to random port.')


def create_rep_socket_bound_to_random():
    sock = compat.MQ.socket(compat.MQ.REP)
    host = 'tcp://127.0.0.1'
    port = _bind_to_random_port(sock, host)
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
