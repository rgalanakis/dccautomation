"""
Mixin classes for different system tests that may be used
under different environments or configurations.
"""

from dccautomation import compat, utils, Closed, InvalidMethod, Timeout


# noinspection PyPep8Naming
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
        with self.assertRaises(Timeout):
            self.client.exec_('import time; time.sleep(0.1)')

    def test_invalid_method(self):
        with self.assertRaises(InvalidMethod):
            self.client.sendrecv(['abc', 1])

    def test_close(self):
        cl = self.new_client()
        self.assertFalse(utils.is_open(cl.serverproc.endpoint))
        cl.close_all()
        with self.assertRaises(Closed):
            cl.exec_('1')
        self.assertTrue(utils.is_open(cl.serverproc.endpoint))

    def test_skipped_is_reraised_and_not_an_error(self):
        with self.assertRaises(compat.unittest.SkipTest):
            self.client.exec_('import dccautomation.compat as c;'
                              'raise c.unittest.SkipTest()')
