from .. import mayaauto


class MayaTests(mayaauto.MayaTestCase):

    def test_is_in_maya(self):
        self.assertTrue(mayaauto.MAYA)

    def test_pymel(self):
        mayaauto.pmc.polySphere()
