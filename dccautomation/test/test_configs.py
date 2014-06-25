from .. import _compat, configs


class UnsupportedConfigTests(_compat.unittest.TestCase):

    def test_raises_on_call(self):
        with self.assertRaises(configs.UnsupportedConfig):
            configs.UnsupportedConfig('foo')()
