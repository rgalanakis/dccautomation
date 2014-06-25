import exceptions
import time
import zmq

from . import common


class UnhandledError(RuntimeError):
    pass


class InvalidMethod(RuntimeError):
    pass


class UnhandledResponse(RuntimeError):
    pass


class Timeout(RuntimeError):
    pass


class Closed(RuntimeError):
    pass


class Client(object):
    def __init__(self, serverproc, timeout_secs=50.0):
        self.serverproc = serverproc
        self.timeout_secs = timeout_secs
        self.socket = self._create_socket()
        self._closed = False

    def _create_socket(self):
        socket = zmq.Context().socket(zmq.REQ)
        socket.connect(self.serverproc.endpoint)
        return socket

    def sendrecv(self, data):
        if self._closed:
            raise Closed()
        self.socket.send(self.serverproc.config.dumps(data))
        starttime = time.time()
        while True:
            try:
                recved = self.socket.recv(zmq.NOBLOCK)
                break
            except zmq.Again:
                if time.time() - starttime > self.timeout_secs:
                    self.socket = self._create_socket()
                    raise Timeout('Timed out after %ss' % self.timeout_secs)
                time.sleep(0.1)

        # noinspection PyUnboundLocalVariable
        response = self.serverproc.config.loads(recved)
        code = response['code']
        if code == common.SUCCESS:
            return response['value']
        if code == common.INVALID_METHOD:
            raise InvalidMethod('Sent invalid method: %s' % response['value'])
        if code == common.UNHANDLED_ERROR:
            errtype = getattr(exceptions, response['errtype'], UnhandledError)
            raise errtype(response['traceback'])
        raise UnhandledResponse('Unhandled response: %s, %s' % (
            code, response))

    def eval_(self, s):
        return self.sendrecv(['eval', s])

    def exec_(self, s):
        return self.sendrecv(['exec', s])

    def close_all(self):
        self.sendrecv(['close', ''])
        self.socket.close()
        self._closed = True
