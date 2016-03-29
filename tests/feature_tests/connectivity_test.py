from tests.feature_tests.test_server import TestServer
from src.DeepStreamClient import DeepStreamClient
from src import Constants as C

import pytest
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
        client._connection.close()

    def test_client_receives_invalid_authentication_data(self):
        client = DeepStreamClient("127.0.0.1", 9999)
        credentials = {}
        credentials["username"] = "XXX"
        credentials["password"] = "YYY"
        client.login(credentials, None)
        self.server.send(C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ERROR + C.MESSAGE_PART_SEPARATOR + "INVALID_AUTH_DATA" + C.MESSAGE_PART_SEPARATOR + "Sinvalid authentication data" + C.MESSAGE_SEPARATOR)
        time.sleep(1)
        assert client.get_connection_state() == C.CONNECTION_STATE_AWAITING_AUTHENTICATION
        client._connection.close()

    def test_client_made_too_many_unsuccessful_authentication_attempts(self):
        client = DeepStreamClient("127.0.0.1", 9999)
        credentials = {}
        credentials["username"] = "user_too_many_auth"
        credentials["password"] = "pass_too_many_auth"
        client.login(credentials, None)
        time.sleep(1)
        self.server.send(C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ERROR + C.MESSAGE_PART_SEPARATOR + "TOO_MANY_AUTH_ATTEMPTS" + C.MESSAGE_SEPARATOR)
        assert client.get_connection_state() == C.CONNECTION_STATE_AUTHENTICATING
        client._connection.close()

    def test_client_cant_connect_after_TOO_MANY_AUTH_ATTEMPTS(self):
        client = DeepStreamClient("127.0.0.1", 9999)
        credentials = {}
        credentials["username"] = "user_too_many_auth"
        credentials["password"] = "pass_too_many_auth"
        client.login(credentials, None)
        time.sleep(1)
        self.server.send(C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ERROR + C.MESSAGE_PART_SEPARATOR + "TOO_MANY_AUTH_ATTEMPTS" + C.MESSAGE_SEPARATOR)
        time.sleep(1)

        with pytest.raises(Exception) as excinfo:
            client.login(credentials, None)

        assert 'client\'s connection was closed' in str(excinfo.value)

    @classmethod
    def teardown_class(cls):
        cls.server.stop()
        try:
            cls.server_thread.join(1)
        except Exception as e:
            print(e)


