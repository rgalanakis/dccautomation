import atexit
import os
import subprocess
import zmq

from .. import config, Client, mayaauto, testcase


def start_maya_server():
    env = dict(os.environ)
    env['PYTHONPATH'] += '{sep}{}{sep}{}'.format(
        os.path.dirname(config.__file__),
        os.path.dirname(os.path.dirname(zmq.__file__)),
        sep=os.path.pathsep)
    proc = subprocess.Popen(config.mayaproc_test_args, env=env)
    atexit.register(proc.kill)
    client = Client(config.host, config.port)
    return proc, client


class MayaTests(testcase.RemoteTestCase):

    @classmethod
    def create_client(cls):
        assert not mayaauto.MAYA
        return start_maya_server()[1]

    def test_is_in_maya(self):
        self.assertTrue(mayaauto.MAYA)

    def test_pymel(self):
        mayaauto.pmc.polySphere()
