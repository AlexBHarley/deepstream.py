from tests.feature_tests.test_server import TestServer
from src.DeepStreamClient import DeepStreamClient
from src import Constants as C
from src.message import MessageBuilder

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
        assert client.get_connection_state() == C.CONNECTION_STATE_AWAITING_AUTHENTICATION
        client._connection.close()

    @classmethod
    def teardown_class(cls):
        cls.server.stop()
        try:
            cls.server_thread.join(1)
        except Exception as e:
            print(e)


class TestAuthenticatingAClient:

    @classmethod
    def setup_class(cls):
        cls.server = TestServer("127.0.0.1", 9999)
        cls.server_thread = threading.Thread(target=cls.server.start_listening)
        cls.server_thread.setDaemon(True)
        cls.server_thread.start()

    def test_client_sends_login_credentials(self):
        client = DeepStreamClient("127.0.0.1", 9999)
        credentials = {}
        credentials["username"] = "XXX"
        credentials["password"] = "YYY"
        client.login(credentials, None)
        time.sleep(1)
        msg = self.server.last_message
        auth_msg = C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_REQUEST + C.MESSAGE_PART_SEPARATOR + "{\"password\": \"YYY\", \"username\": \"XXX\"}" + C.MESSAGE_SEPARATOR
        assert msg == str.encode(auth_msg)
        client._connection.close()

    def test_client_receives_login_confirmation(self):
        client = DeepStreamClient("127.0.0.1", 9999)
        credentials = {}
        credentials["username"] = "XXX"
        credentials["password"] = "YYY"
        client.login(credentials, None)
        self.server.send(C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_SEPARATOR)
        time.sleep(1)
        assert C.CONNECTION_STATE_OPEN == client.get_connection_state()
        client._connection.close()

    def test_client_receives_invalid_authentication_message(self):
        client = DeepStreamClient("127.0.0.1", 9999)
        credentials = {}
        credentials["username"] = "XXX"
        credentials["password"] = "YYY"
        client.login(credentials, None)
        self.server.send(C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ERROR + C.MESSAGE_PART_SEPARATOR + "INVALID_AUTH_MSG" + C.MESSAGE_PART_SEPARATOR + "Sinvalid" + C.MESSAGE_SEPARATOR)
        time.sleep(1)
        assert client.get_connection_state() == C.CONNECTION_STATE_AWAITING_AUTHENTICATION

        '''
Scenario: The client's authentication data is rejected
	Given the client is initialised
	When the client logs in with username "XXX" and password "ZZZ"
		But the server sends the message A|E|INVALID_AUTH_DATA|Sinvalid authentication data+
	Then the last login failed with error "INVALID_AUTH_DATA" and message "invalid authentication data"

Scenario: The client has made too many unsuccessful authentication attempts
	Given the client is initialised
	When the client logs in with username "XXX" and password "ZZZ"
		But the server sends the message A|E|TOO_MANY_AUTH_ATTEMPTS|Stoo many authentication attempts+
	Then the last login failed with error "TOO_MANY_AUTH_ATTEMPTS" and message "too many authentication attempts"

Scenario: The client can't made further authentication attempts after it received TOO_MANY_AUTH_ATTEMPTS
	Given the server resets its message count
	When the client logs in with username "XXX" and password "ZZZ"
	Then the server has received 0 messages
		And the client throws a "IS_CLOSED" error with message "this client's connection was closed"
    '''

    @classmethod
    def teardown_class(cls):
        cls.server.stop()
        try:
            cls.server_thread.join(1)
        except Exception as e:
            print(e)