from .. import configs, mayaauto, testcase


class MayaTests(testcase.RemoteTestCase):

    config = configs.Maya

    def test_is_in_maya(self):
        self.assertTrue(mayaauto.MAYA)

    def test_pymel(self):
        mayaauto.pmc.polySphere()
