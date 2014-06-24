import exceptions
import time
import zmq

from . import statuscodes


class UnhandledError(RuntimeError):
    pass


class InvalidMethod(RuntimeError):
    pass


class UnhandledResponse(RuntimeError):
    pass


class Client(object):
    def __init__(self, config, timeout_secs=50.0):
        self.config = config
        self.timeout_secs = timeout_secs
        self.socket = self._create_socket()

    def _create_socket(self):
        socket = zmq.Context().socket(zmq.REQ)
        socket.connect('tcp://%s:%s' % (self.config.host, self.config.port))
        return socket

    def sendrecv(self, data):
        self.socket.send(self.config.dumps(data))
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
        response = self.config.loads(recved)
        code = response['code']
        if code == statuscodes.SUCCESS:
            return response['value']
        if code == statuscodes.INVALID_METHOD:
            raise InvalidMethod('Sent invalid method: %s' % response['value'])
        if code == statuscodes.UNHANDLED_ERROR:
            errtype = getattr(exceptions, response['errtype'], UnhandledError)
            raise errtype(response['traceback'])
        raise UnhandledResponse('Unhandled response: %s, %s' % (
            code, response))

    def eval_(self, s):
        return self.sendrecv(['eval', s])

    def exec_(self, s):
        return self.sendrecv(['exec', s])
