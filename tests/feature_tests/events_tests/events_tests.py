from tests.feature_tests.test_server import start_server, TestServer
from src.DeepStreamClient import DeepStreamClient
from src import Constants as C

import threading
import time


class TestEventConnection:
    @classmethod
    def setup_class(cls):
        cls.server = TestServer()
        cls.server_thread = threading.Thread(target=start_server, args=(cls.server,))
        cls.server_thread.start()

    def test_client_subscribes_to_event(self):
        '''
        Scenario: The client subscribes to an event
            Given the client subscribes to an event named "test1"
            Then the last message the server received is E|S|test1+
        	Then the server sends the message E|A|S|test1+
        '''
        time.sleep(1)
        client = DeepStreamClient("127.0.0.1", 8888)
        credentials = {}
        credentials["username"] = "valid_username"
        credentials["password"] = "valid_password"
        client.login(credentials, None)
        time.sleep(1)

        client.event.subscribe("test1", None)
        time.sleep(1)
        subscribe_message = str.encode(C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_SUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR)
        assert self.server.last_message == subscribe_message
        client._connection.close()

    def test_client_unsubscribes_to_event(self):
        client = DeepStreamClient("127.0.0.1", 13999)
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

    def test_client_listens_to_event_prefix(self):
        '''
        Scenario: The client listens to eventPrefix
            When the client listens to events matching "eventPrefix/.*"
            Then the last message the server received is E|L|eventPrefix/.*+
	        Then the server sends the message E|A|L|eventPrefix/.*+
	    '''
        client = DeepStreamClient("127.0.0.1", 13999)
        credentials = {}
        credentials["username"] = "valid_username"
        credentials["password"] = "valid_password"
        client.login(credentials, None)
        time.sleep(1)
        client.event.listen("regex/\*", None)
        time.sleep(1)
        assert self.server.last_message == str.encode(
            C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_LISTEN + C.MESSAGE_PART_SEPARATOR + "regex/\*" + C.MESSAGE_SEPARATOR
        )
        client._connection.close()

    @classmethod
    def teardown_class(cls):
        try:
            cls.server_thread.join()
        except Exception as e:
            print(e)

'''




Scenario: The client loses its connection to the server
	When the connection to the server is lost
	Given two seconds later
	Then the client throws a "connectionError" error with message "Can't connect! Deepstream server unreachable on localhost:7777"
		And the clients connection state is "RECONNECTING"

Scenario: The client publishes an event
	When the client publishes an event named "test1" with data "yetAnotherValue"
	Then the server did not recieve any messages

Scenario: The client reconnects to the server
	When the connection to the server is reestablished
	Then the clients connection state is "AUTHENTICATING"

Scenario: The client successfully reconnects
	Given the client logs in with username "XXX" and password "YYY"
		And the server sends the message A|A+
	Then the clients connection state is "OPEN"

Scenario: The client resends the event subscription
	Then the server received the message E|S|test1+

Scenario: The client resends the event listen
	Then the server received the message E|L|eventPrefix/.*+

Scenario: The client sends offline events
	Then the server received the message E|EVT|test1|SyetAnotherValue+'''