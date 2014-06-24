from .. import testcase
from . import start_test_server


class TestcaseTests(testcase.RemoteTestCase):

    @classmethod
    def create_client(cls):
        proc, client = start_test_server()
        return client

    def test_foo(self):
        self.assertTrue(True)
