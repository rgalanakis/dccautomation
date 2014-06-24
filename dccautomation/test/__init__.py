"""
Tests for dccautomation.

The tests are included with the code because clients may be interested in
creating their own test cases using the dccautomation tests.
"""

import atexit
import os
import subprocess
import zmq

from .. import Client, __file__ as dccpkg_file


def _one_up_dir(f):
    return os.path.dirname(os.path.dirname(f))


def start_test_server(config):

    env = dict(os.environ)
    env['PYTHONPATH'] += '{sep}{}{sep}{}'.format(
        _one_up_dir(dccpkg_file),
        _one_up_dir(zmq.__file__),
        sep=os.path.pathsep)
    proc = subprocess.Popen(config.popen_args(), env=env)
    atexit.register(proc.kill)
    client = Client(config)
    return proc, client
