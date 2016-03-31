from tests.feature_tests.test_server import TestServer
from src.DeepStreamClient import DeepStreamClient
from src import Constants as C

import pytest
import threading
import time

class TestEvents:
    @classmethod
    def setup_class(cls):
        cls.server = TestServer("127.0.0.1", 9999)
        cls.server_thread = threading.Thread(target=cls.server.start_listening)
        cls.server_thread.setDaemon(True)
        cls.server_thread.start()

    def test_client_subscribes_to_event(self):
        client = DeepStreamClient("127.0.0.1", 9999)
        credentials = {}
        credentials["username"] = "XXX"
        credentials["password"] = "YYY"
        client.login(credentials, None)
        x = ''

        def catch(msg):
            x = msg

        client.event.subscribe("test1", catch)

        assert self.server.last_message == str.encode(C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_SUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR)

        self.server.send(C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_SUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR)
        assert x == "test1"

    @classmethod
    def teardown_class(cls):
        cls.server.stop()
        try:
            cls.server_thread.join(1)
        except Exception as e:
            print(e)

'''
Scenario: The server sends an ACK message for test1
	Given the server sends the message E|A|S|test1+
	'''