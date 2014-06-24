import sys
import traceback

from . import configs, Client
from ._compat import unittest


class RemoteTestCase(unittest.TestCase):
    """
    Subclass for test classes which should execute in the DCC process.
    This is sort of magical, and you can generally stay out of it
    by overriding this class and some of its attributes::

    - config: A subclass of :class:`dccautomation.configs.Config`.
      Do *not* use an instance of it.
    - reload_test: If True, reload the test file before running each test.
    - cache_client: If True, use one client for all test methods.
        If False, use a new client for each test.
        Clients are created through the :meth:`create_client` method.
    - start_proc: If True, start a server process before creating the client.

    Most of this behavior is used in the :meth:`create_client` method.
    Override this method for advanced usage.
    """
    config = None
    reload_test = True
    cache_client = True
    start_proc = True
    _cached_client = None
    __testMethodName = None

    @classmethod
    def create_client(cls):
        """
        :rtype: dccautomation.client.Client
        """
        if cls.config is None:
            raise RuntimeError(
                'config must be set or this method must be overridden.')
        config = cls.config()
        if cls.start_proc:
            configs.start_server_process(config)
        return Client(config)

    @classmethod
    def _get_client(cls):
        if not cls.cache_client:
            return cls.create_client()
        if cls._cached_client is None:
            cls._cached_client = cls.create_client()
        return cls._cached_client

    def run(self, result=None):
        try:
            client = self._get_client()
        except Exception:
            sys.stderr.write('Critical failure creating client for test:\n')
            sys.stderr.write('%s.%s' % (
                type(self).__name__, self._testMethodName))
            traceback.print_exc()
            raise

        def wrapped_test():
            # We must only change self._testMethodName while running
            # the actual test,
            # or the reporting of our test will have the wrong name.
            self.__testMethodName = self._testMethodName
            try:
                self._wrapped_test(client)
            finally:
                self._testMethodName = self.__testMethodName
                # setup and teardown should never call a subclass version,

        # since they should only run on the server.
        # noinspection PyAttributeOutsideInit
        self.setUp, self.tearDown = lambda *a: None, lambda *a: None
        setattr(self, self._testMethodName, wrapped_test)
        unittest.TestCase.run(self, result)

    def _wrapped_test(self, client):
        # Tell the server to execute the test.
        # Running the test this way will propogate problems
        # (unlike 'run', which adjusts the test result).
        # We can look in the future at creating some sort of
        # pickle-able test result, which would in theory be safer.
        teststr = 'import {testmodule} as {testalias}\n'
        if self.reload_test:
            teststr += 'reload({testalias})\n'
        teststr += """tc = {testalias}.{testcase}("{testfunc}")
try:
    tc.setUp()
    tc.{testfunc}()
finally:
    tc.tearDown()"""
        teststr = teststr.format(
            testmodule=self.__module__,
            testalias=self.__module__.replace('.', '_'),
            testcase=type(self).__name__,
            testfunc=self.__testMethodName)
        client.exec_(teststr)
