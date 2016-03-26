from tests.feature_tests.test_server import TestServer
from src.DeepStreamClient import DeepStreamClient
from contexts import setup, assertion, teardown
import unittest
import threading
import time

class WhenConnectingAClient:

    def __init__(self):
        self.server = TestServer('127.0.0.1', 5462)

    @setup
    def given_a_test_server(self):
        self.server_thread = threading.Thread(target=self.server.start_listening)
        self.server_thread.daemon = True
        try:
            self.server_thread.start()
        except Exception:
            pass

    @assertion
    def test_server_is_ready(self):
        assert self.server.is_ready == True

    @assertion
    def server_has_no_active_connections(self):
        assert (len(self.server.connections) == 0)



    @assertion
    def client_is_initialised(self):
        self.client = DeepStreamClient('127.0.0.1', 5462)
        assert (self.client != None)

    @teardown
    def teardown(self):
        self.server.stop()
        #self.client._connection._endpoint.join()
        try:
            self.server_thread.join(1)
        except Exception:
            pass
'''
    @assertion
    def server_has_an_active_connection(self):
        assert len(self.server.connections) == 1

    @assertion
    def client_connection_state_is_AWAITING_AUTHENTICATION(self):
        assert (self.client._state == "AWAITING_AUTHENTICATION")'''


