import sys
import traceback
import unittest


class RemoteTestCase(unittest.TestCase):
    _cached_client = None
    cache_client = True
    reload_test = True
    __testMethodName = None

    @classmethod
    def create_client(cls):
        """
        :rtype: dccautomation.client.Client
        """
        raise NotImplementedError()

    @classmethod
    def _create_client(cls):
        if cls._cached_client is None:
            c = cls.create_client()
        if cls.cache_client:
            # noinspection PyUnboundLocalVariable
            cls._cached_client = c
        return c

    def run(self, result=None):
        try:
            client = self._create_client()
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
        self.setUp = lambda *a: None
        self.tearDown = lambda *a: None
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
