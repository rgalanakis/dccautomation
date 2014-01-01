from dccautomation import configs, RemoteTestCase


class TestcaseTests(RemoteTestCase):
    """
    There's no good test for this yet.
    This is just a stub.
    We really need a DCC app set up to verify we're not in Python.
    Then we can test the DCC-specific RemoteTestCase subclasses.
    """

    config = configs.CurrentPython

    def test_works(self):
        self.assertTrue(True)
