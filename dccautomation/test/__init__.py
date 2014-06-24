"""
Tests for dccautomation.

The tests are included with the code because clients may be interested in
creating their own test cases using the dccautomation tests.
"""

import atexit
import os
import subprocess
import zmq

from .. import config, Client


def start_test_server():

    env = dict(os.environ)
    env['PYTHONPATH'] += '{sep}{}{sep}{}'.format(
        os.path.dirname(config.__file__),
        os.path.dirname(os.path.dirname(zmq.__file__)),
        sep=os.path.pathsep)
    proc = subprocess.Popen(config.tester_proc_args, env=env)
    atexit.register(proc.kill)
    client = Client(config.host, config.port)
    return proc, client
