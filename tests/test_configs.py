from dccautomation import compat, configs


class UnsupportedConfigTests(compat.unittest.TestCase):

    def test_raises_on_call(self):
        with self.assertRaises(configs.UnsupportedConfig):
            configs.UnsupportedConfig('foo')()


class ConfigByNameTests(compat.unittest.TestCase):

    def test_raises_if_not_found(self):
        with self.assertRaises(configs.UnsupportedConfig):
            configs.config_by_name('SpamEggs')

    def test_finds(self):
        cfg = configs.config_by_name(configs.CurrentPython.__name__)
        self.assertIsInstance(cfg, configs.CurrentPython)


class TestClassProperty(compat.unittest.TestCase):

    def test_exe_behavior(self):
        class Foo(object):
            @configs.classproperty
            def exe(self):
                return 'foo'

        self.assertEqual(Foo().exe, 'foo')
        self.assertEqual(Foo.exe, 'foo')
