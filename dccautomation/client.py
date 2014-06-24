import time
import zmq

from . import config


class UnhandledError(RuntimeError):
    pass


class InvalidMethod(RuntimeError):
    pass


class UnhandledResponse(RuntimeError):
    pass


class Client(object):
    def __init__(self, host, port, timeout_secs=50.0):
        self.host = host
        self.port = port
        self.timeout_secs = timeout_secs
        self.socket = self._create_socket()

    def _create_socket(self):
        socket = zmq.Context().socket(zmq.REQ)
        socket.connect('tcp://%s:%s' % (self.host, self.port))
        return socket

    def sendrecv(self, data):
        self.socket.send(config.dumps(data))
        starttime = time.time()
        while True:
            try:
                recved = self.socket.recv(zmq.NOBLOCK)
                break
            except zmq.Again:
                if time.time() - starttime > self.timeout_secs:
                    self.socket = self._create_socket()
                    raise
                time.sleep(0.1)

        # noinspection PyUnboundLocalVariable
        code, response = config.loads(recved)

        if code == config.SUCCESS:
            return response
        if code == config.UNHANDLED_ERROR:
            raise UnhandledError(response)
        if code == config.INVALID_METHOD:
            raise InvalidMethod('Sent invalid method: %s' % response)
        raise UnhandledResponse('Unhandled response: %s, %s' % (
            code, response))

    def eval_(self, s):
        return self.sendrecv(['eval', s])

    def exec_(self, s):
        return self.sendrecv(['exec', s])
