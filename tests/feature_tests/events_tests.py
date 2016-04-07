from tests.feature_tests.test_server import TServer
from src.DeepStreamClient import DeepStreamClient
from src import Constants as C

import pytest
import threading
import time

class TestEvents:
    @classmethod
    def setup_class(cls):
        cls.server = TServer("127.0.0.1", 13999)
        cls.server_thread = threading.Thread(target=cls.server.start)
        cls.server_thread.setDaemon(True)
        cls.server_thread.start()

    def test_client_subscribes_to_event(self):
        time.sleep(1)
        client = DeepStreamClient("127.0.0.1", 13999)
        credentials = {}
        credentials["username"] = "valid_username"
        credentials["password"] = "valid_password"
        client.login(credentials, None)
        time.sleep(1)

        client.event.subscribe("test1", None)
        time.sleep(1)
        assert self.server.last_message == str.encode(C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_SUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR)
        client._connection.close()
    '''
    def test_client_unsubscribes_to_event(self):
        client = DeepStreamClient("127.0.0.1", 9999)
        credentials = {}
        credentials["username"] = "valid_username"
        credentials["password"] = "valid_password"
        client.login(credentials, None)
        time.sleep(1)

        client.event.unsubscribe("test1", None)
        time.sleep(1)
        assert self.server.last_message == str.encode(
            C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_UNSUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR)
        client._connection.close()
    '''
    @classmethod
    def teardown_class(cls):
        try:
            cls.server_thread.join(0)
        except Exception as e:
            print(e)
