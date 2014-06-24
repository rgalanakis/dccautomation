"""
System-level tests.
"""
import os
import subprocess
import unittest
import zmq

from .. import config, Client


class SystemTests(unittest.TestCase):
    proc = None

    @classmethod
    def setUpClass(cls):
        env = dict(os.environ)
        env['PYTHONPATH'] += '{sep}{}{sep}{}'.format(
            os.path.dirname(config.__file__),
            os.path.dirname(os.path.dirname(zmq.__file__)),
            sep=os.path.pathsep)
        cls.proc = subprocess.Popen(config.tester_proc_args, env=env)
        cls.client = Client(config.host, config.port)

    @classmethod
    def tearDownClass(cls):
        cls.proc.kill()

    def test_is_another_proc(self):
        self.client.exec_('import os')
        got = self.client.eval_('os.getpid()')
        self.assertNotEqual(got, os.getpid())

    def test_eval(self):
        got = self.client.eval_('1 + 1')
        self.assertEqual(got, 2)

    def test_exec(self):
        self.client.exec_('a = 2 + 1')
        got = self.client.eval_('a')
        self.assertEqual(got, 3)

    def test_errortype_propagates(self):
        with self.assertRaises(TypeError):
            self.client.exec_('1 + ""')
