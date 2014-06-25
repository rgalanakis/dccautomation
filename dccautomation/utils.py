import zmq


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
