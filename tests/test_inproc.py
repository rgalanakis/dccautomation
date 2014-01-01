import mock

from dccautomation import compat, common, inproc


class DefaultPortTests(compat.unittest.TestCase):

    def test_default(self):
        self.assertEqual(inproc.get_default_port(), inproc.DEFAULT_INPROC_PORT)

    def test_non_default(self):
        with mock.patch('os.environ', {common.ENV_INPROC_PORT: '20'}):
            self.assertEqual(inproc.get_default_port(), 20)
