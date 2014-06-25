from .. import _compat, configs


class UnsupportedConfigTests(_compat.unittest.TestCase):

    def test_raises_on_call(self):
        with self.assertRaises(configs.UnsupportedConfig):
            configs.UnsupportedConfig('foo')()


class ConfigByNameTests(_compat.unittest.TestCase):

    def test_raises_if_not_found(self):
        with self.assertRaises(configs.UnsupportedConfig):
            configs.config_by_name('SpamEggs')

    def test_finds(self):
        cfg = configs.config_by_name(configs.CurrentPython.__name__)
        self.assertIsInstance(cfg, configs.CurrentPython)
