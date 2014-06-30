"""
All client-only code.
"""

import exceptions
import time
import zmq

from . import common, utils


class UnhandledError(RuntimeError):
    """An unhandled error occured on the server."""
    pass


class InvalidMethod(RuntimeError):
    """The client asked the server to perform a method it did not understand.
    """
    pass


class UnhandledResponse(RuntimeError):
    """The server sent the client a response the client did not understand."""
    pass


class Timeout(RuntimeError):
    """The server did not respond in time."""
    pass


class Closed(RuntimeError):
    """The client has already closed (and the server is already likely
    shut down)."""
    pass


class Client(object):
    """
    Encapsulates everything the client can ask the server to do.

    :type serverproc: dccautomation.bootstrap.ServerProc
    """
    def __init__(self, serverproc, timeout_secs=50.0):
        self.logger = utils.logger(__name__, serverproc.endpoint)
        self.serverproc = serverproc
        self.timeout_secs = timeout_secs
        self.socket = self._create_socket()
        self._closed = False

    def _create_socket(self):
        socket = zmq.Context().socket(zmq.REQ)
        socket.connect(self.serverproc.endpoint)
        return socket

    def sendrecv(self, data):
        """
        Send data to the server and process the server's response.
        """
        if self._closed:
            raise Closed()
        self.logger.debug('send: %s', data)
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
        self.logger.debug('recv: %s', response)
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
        """Evaluate the given string in global scope on the server,
        and return the result."""
        return self.sendrecv(['eval', s])

    def exec_(self, s):
        """Execute the given string in a global scope on the server."""
        return self.sendrecv(['exec', s])

    def close_all(self):
        """
        Ask the server loop to exit (possibly exiting the server process),
        and close the client socket.
        No further operations can be done after this.
        """
        self.sendrecv(['close', ''])
        self.socket.close()
        self._closed = True
