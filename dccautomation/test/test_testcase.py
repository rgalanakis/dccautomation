from .. import configs, testcase


class TestcaseTests(testcase.RemoteTestCase):

    config = configs.CurrentPython

    def test_foo(self):
        self.assertTrue(True)
