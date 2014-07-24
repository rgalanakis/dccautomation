from dccautomation import compat, configs, RemoteTestCase


class _TestcaseTests(RemoteTestCase):
    """
    There's no good test for this yet.
    This is just a stub.
    We really need a DCC app set up to verify we're not in Python.
    Then we can test the DCC-specific RemoteTestCase subclasses.
    """

    config = configs.CurrentPython

    def success(self):
        self.assertTrue(True)

    def error(self):
        raise NotImplementedError('This is an error.')

    def failure(self):
        self.assertFalse(True, 'This is a failure.')


class TestcaseTests(compat.unittest.TestCase):

    def runit(self, name):
        r = self.defaultTestResult()
        _TestcaseTests(name).run(r)
        return r

    def test_success(self):
        r = self.runit('success')
        self.assertTrue(r.wasSuccessful())

    def test_error(self):
        r = self.runit('error')
        self.assertEqual(len(r.errors), 1)
        self.assertFalse(r.failures)

    def test_failure(self):
        r = self.runit('failure')
        self.assertEqual(len(r.failures), 1)
        self.assertFalse(r.errors)
