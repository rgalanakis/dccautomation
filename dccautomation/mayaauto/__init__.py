MAYA = False
maya = None
pmc = None

try:
    import maya
    import pymel.core as pmc
    MAYA = True
except ImportError:
    MAYA = False
    maya = None
    pmc = None


from .. import configs, testcase


class MayaTestCase(testcase.RemoteTestCase):
    config = configs.Maya