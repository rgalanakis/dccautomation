from dccautomation import compat, utils


class LoggerTests(compat.unittest.TestCase):

    def test_all(self):
        def assert_result(endpoint, ideal):
            log = utils.logger('a.b', endpoint)
            self.assertEqual(log.name, ideal)
        assert_result('tcp://localhost:8080', 'a.b.lo-8080')
        assert_result('tcp://127.0.0.1:8080', 'a.b.lo-8080')
        assert_result('tcp://1.2.3.4:50', 'a.b.1_2_3_4-50')


class IsOpenTests(compat.unittest.TestCase):

    def test_all(self):
        conninfo = utils.create_rep_socket_bound_to_random()
        utils.assert_open(conninfo, False)
        conninfo.socket.close()
        # We cannot reliably assert a socket is open after its closed,
        # because it could have been bound.
        # utils.assert_open(conninfo)
