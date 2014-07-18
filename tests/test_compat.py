from __future__ import print_function
import subprocess
import sys
import unittest

from dccautomation import bootstrap, compat, utils


class BackendTests(unittest.TestCase):

    def test_uninitialized_socket_behavior(self):
        # Verify that errors are raised when recv on an unconnected REQ
        # or sending on an unbound REP,
        # and uninitialized sockets can be closed.
        s = compat.MQ.socket(compat.MQ.REQ)
        self.assertRaises(compat.MQ.errtype, s.recv)
        s.close()

        s = compat.MQ.socket(compat.MQ.REP)
        self.assertRaises(compat.MQ.errtype, s.send, b'1')
        s.close()

    def test_invalid_socket_type(self):
        self.assertRaises(ValueError, compat.MQ.socket, -18484)

    def test_rebind_fails(self):
        if not compat.MQ.safe_to_rebind():
            raise unittest.SkipTest('Test is not safe to run.')
        s1 = utils.create_rep_socket_bound_to_random()
        s2 = compat.MQ.socket(compat.MQ.REP)
        self.assertRaises(compat.MQ.errtype, s2.bind, s1.endpoint)

    def test_bound_socket_is_cleaned_up_in_subproc(self):
        """Make sure that even in the event of a termination,
        the socket can be rebound and doesn't leave some dangling state
        like a file pointer."""
        args = [
            sys.executable,
            '-c',
            'import tests.test_compat as tc; tc.bind_and_wait()']
        p = bootstrap.start_process(
            args, stdout=subprocess.PIPE)
        endpoint = p.stdout.readline().strip().decode('utf-8')
        p.kill()
        p.wait()
        self.assertTrue(p.returncode)
        s = compat.MQ.socket(compat.MQ.REP)
        s.bind(endpoint)


def bind_and_wait():
    s = utils.create_rep_socket_bound_to_random()
    print(s.endpoint)
    while True:
        print('')


class CalcBackendTests(unittest.TestCase):

    def test_unknown(self):
        self.assertRaises(ValueError, compat.calc_backend, 'WTF')

    def test_no_matching(self):
        self.assertRaises(ImportError, compat.calc_backend, '', [])
