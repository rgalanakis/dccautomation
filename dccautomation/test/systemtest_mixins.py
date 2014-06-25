"""
Mixin classes for different system tests that may be used
under different environments or configurations.
"""
import zmq

from .. import client


def try_bind(endpoint):
    try:
        sock = zmq.Context().socket(zmq.REP)
        sock.bind(endpoint)
        sock.close()
    except zmq.ZMQError:
        raise zmq.ZMQError('Endpoint %s already bound.' % endpoint)


# noinspection PyUnresolvedReferences,PyPep8Naming
class SystemTests(object):

    @classmethod
    def setUpClass(cls):
        cls.client = cls.new_client()

    @classmethod
    def new_client(cls):
        raise NotImplementedError()

    def test_eval(self):
        got = self.client.eval_('1 + 1')
        self.assertEqual(got, 2)

    def test_exec(self):
        self.client.exec_('a = 2 + 1')
        got = self.client.eval_('a')
        self.assertEqual(got, 3)

    def test_errortype_propagates(self):
        with self.assertRaises(TypeError):
            self.client.exec_('1 + ""')

    def test_timeout(self):
        self.client.timeout_secs = 0.0
        with self.assertRaises(client.Timeout):
            self.client.exec_('import time; time.sleep(0.1')

    def test_invalid_method(self):
        with self.assertRaises(client.InvalidMethod):
            self.client.sendrecv(['abc', 1])

    def test_close(self):
        cl = self.new_client()

        with self.assertRaises(zmq.ZMQError):
            try_bind(cl.serverproc.endpoint)
        cl.close_all()
        with self.assertRaises(client.Closed):
            cl.exec_('1')
        try_bind(cl.serverproc.endpoint)
