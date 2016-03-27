from tests.feature_tests.test_server import TestServer
from src.DeepStreamClient import DeepStreamClient
from src import Constants
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
        assert client._ip == "127.0.0.1"
        assert client._port == 9999
        time.sleep(1) #allow time for client to connect
        assert self.server.connection_count == 1
        assert client.get_connection_state() == Constants.CONNECTION_STATE_AWAITING_AUTHENTICATION
        client._connection.close()

    @classmethod
    def teardown_class(cls):
        cls.server.stop()
        try:
            cls.server_thread.join(1)
        except Exception as e:
            print(e)
