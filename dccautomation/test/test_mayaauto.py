import atexit
import os
import subprocess
import zmq

from .. import configs, Client, mayaauto, testcase



class MayaTests(testcase.RemoteTestCase):

    @classmethod
    def create_client(cls):
        assert not mayaauto.MAYA
        return start_maya_server()[1]

    def test_is_in_maya(self):
        self.assertTrue(mayaauto.MAYA)

    def test_pymel(self):
        mayaauto.pmc.polySphere()
