from tests.feature_tests.test_server import ServerThread, TestServer
from src.DeepStreamClient import DeepStreamClient
from contexts import setup, assertion, teardown
import unittest


class WhenConnectingAClient:

    def __init__(self):
        self.server_thread = None

    @setup
    def given_a_test_server(self):
        self.server_thread = ServerThread('127.0.0.1', 5555)
        self.server_thread.start()

    @assertion
    def test_server_is_ready(self):
        assert self.server_thread.server.is_ready == True
    '''
    @assertion
    def server_has_no_active_connections(self):
        assert (len(self.server_thread.server.connections) == 0)
    '''
    @teardown
    def teardown(self):
        self.server_thread.stop()
'''
    @assertion
    def client_is_initialised(self):
        self.client = DeepStreamClient('127.0.0.1', 6022)

        self.assertTrue(self.client != None)

    @assertion
    def server_has_an_active_connection(self):
        assert len(self.server.connections) == 1

    @assertion
    def client_connection_state_is_AWAITING_AUTHENTICATION(self):
        assert (self.client._state == "AWAITING_AUTHENTICATION")'''


