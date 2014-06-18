"""
Tests for dccautomation.

The tests are included with the code because clients may be interested in creating their
own test cases using the dccautomation tests.
"""

import unittest

import dccautomation


class SystemTests(unittest.TestCase):
    def test_eval(self):
        endpoint = dccautomation.start_server()
        client = dccautomation.HttpClient(endpoint)
        got = client.eval_('1 + 1')
        self.assertEqual(got, 2)