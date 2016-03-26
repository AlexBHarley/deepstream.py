from tests.feature_tests.test_server import TestServer
from src.DeepStreamClient import DeepStreamClient
import threading
import time


class TestConnectingAClient:

    @classmethod
    def setup_class(cls):
        cls.server = TestServer("127.0.0.1", 9999)
        cls.server_thread = threading.Thread(target=cls.server.start_listening)
        cls.server_thread.setDaemon(True)
        cls.server_thread.start()

    def test_server_should_have_0_connections(self):
        assert self.server.connection_count == 0

    def test_when_the_client_is_initialised_server_should_have_an_active_connection(self):
        client = DeepStreamClient("127.0.0.1", 9999)
        assert (client != None)
        time.sleep(1) #allow time for client to connect
        assert self.server.connection_count == 1
        client._connection.close()

    @classmethod
    def teardown_class(cls):
        cls.server.stop()
        try:
            cls.server_thread.join(1)
        except Exception as e:
            print(e)
