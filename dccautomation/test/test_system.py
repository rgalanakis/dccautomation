"""
System-level tests.
"""
import os

from . import start_test_server
from .._compat import unittest


class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = start_test_server()[1]

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
