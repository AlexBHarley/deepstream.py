import src.Constants as C
import time
import pytest

from mocket.mocket import Mocketizer, Mocket, MocketEntry
from src.DeepStreamClient import DeepStreamClient

"""
Feature: Logging In
	As soon as the client is initialised, it creates a connection with
	the server. However the connection is initially in a quarantine
	state until it sends an authentication message. The auth message
	(A|REQ|<JSON authData>) must always be the first message send by
	the client.
"""


class TestAuthenticatingAClient:

    @Mocketizer.wrap
    def test_client_sends_login_credentials(self):
        """
        Scenario: The client sends login credentials
            Given the test server is ready
                And the client is initialised
            When the client logs in with username "XXX" and password "YYY"
            Then the last message the server recieved is A|REQ|{"username":"XXX","password":"YYY"}+
                And the clients connection state is "AUTHENTICATING"
        """
        Mocket.register(MocketEntry(('localhost', 8989), 0))
        ds = DeepStreamClient('localhost', 8989)
        ds.login({"username": "XXX", "password": "YYY"}, None)
        time.sleep(0.1)
        auth_msg = C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_REQUEST + C.MESSAGE_PART_SEPARATOR + "{\"password\": \"YYY\", \"username\": \"XXX\"}" + C.MESSAGE_SEPARATOR
        assert (Mocket.last_request()) == (str(str.encode(auth_msg)))
        assert ds.get_connection_state() == C.CONNECTION_STATE_AUTHENTICATING

    @Mocketizer.wrap
    def test_client_receives_login_confirmation(self):
        """
        Scenario: The client receives a login confirmation
            When the server sends the message A|A+
            Then the clients connection state is "OPEN"
                And the last login was successful
        """
        ack = C.ACTIONS_ACK + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ACK + C.MESSAGE_SEPARATOR
        Mocket.register(MocketEntry(('localhost', 8989), [str.encode(ack)]))
        ds = DeepStreamClient('localhost', 8989)
        ds.login({"username": "XXX", "password": "YYY"}, None)
        time.sleep(0.1)
        assert ds.get_connection_state() == C.CONNECTION_STATE_OPEN

    @Mocketizer.wrap
    def test_client_receives_invalid_authentication_message(self):
        """
        Scenario: The client logs in with an invalid authentication message
            Given the client is initialised
            When the client logs in with username "XXX" and password "YYY"
                But the server sends the message A|E|INVALID_AUTH_MSG|Sinvalid authentication message+
            Then the last login failed with error "INVALID_AUTH_MSG" and message "invalid authentication message"
        """
        invalid_auth_msg = C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ERROR + C.MESSAGE_PART_SEPARATOR + "INVALID_AUTH_MSG" + C.MESSAGE_PART_SEPARATOR + "Sinvalid" + C.MESSAGE_SEPARATOR
        Mocket.register(MocketEntry(('localhost', 8989), [str.encode(invalid_auth_msg)]))
        ds = DeepStreamClient('localhost', 8989)
        ds.login({"username": "XXX", "password": "YYY"}, None)
        time.sleep(0.1)
        assert ds.get_connection_state() == C.CONNECTION_STATE_AWAITING_AUTHENTICATION

    @Mocketizer.wrap
    def test_client_receives_invalid_authentication_data(self):
        """
        Scenario: The client's authentication data is rejected
            Given the client is initialised
            When the client logs in with username "XXX" and password "ZZZ"
                But the server sends the message A|E|INVALID_AUTH_DATA|Sinvalid authentication data+
            Then the last login failed with error "INVALID_AUTH_DATA" and message "invalid authentication data"
        """
        invalid_auth_data = C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ERROR + C.MESSAGE_PART_SEPARATOR + "INVALID_AUTH_DATA" + C.MESSAGE_PART_SEPARATOR + "Sinvalid authentication data" + C.MESSAGE_SEPARATOR
        Mocket.register(MocketEntry(('localhost', 8989), [str.encode(invalid_auth_data)]))
        ds = DeepStreamClient('localhost', 8989)
        ds.login({"username": "XXX", "password": "YYY"}, None)
        time.sleep(0.1)
        assert ds.get_connection_state() == C.CONNECTION_STATE_AWAITING_AUTHENTICATION

    @Mocketizer.wrap
    def test_client_made_too_many_unsuccessful_authentication_attempts(self):
        """
        Scenario: The client has made too many unsuccessful authentication attempts
            Given the client is initialised
            When the client logs in with username "XXX" and password "ZZZ"
                But the server sends the message A|E|TOO_MANY_AUTH_ATTEMPTS|Stoo many authentication attempts+
            Then the last login failed with error "TOO_MANY_AUTH_ATTEMPTS" and message "too many authentication attempts"
        """
        too_many_auth_attempts = C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ERROR + C.MESSAGE_PART_SEPARATOR + "TOO_MANY_AUTH_ATTEMPTS" + C.MESSAGE_SEPARATOR
        Mocket.register(MocketEntry(('localhost', 8989), [str.encode(too_many_auth_attempts)]))
        ds = DeepStreamClient('localhost', 8989)
        ds.login({"username": "XXX", "password": "YYY"}, None)
        time.sleep(0.1)
        assert ds.get_connection_state() == C.CONNECTION_STATE_AUTHENTICATING

    @Mocketizer.wrap
    def test_client_cant_connect_after_TOO_MANY_AUTH_ATTEMPTS(self):
        """
        Scenario: The client can't made further authentication attempts after it received TOO_MANY_AUTH_ATTEMPTS
            Given the server resets its message count
            When the client logs in with username "XXX" and password "ZZZ"
            Then the server has received 0 messages
                And the client throws a "IS_CLOSED" error with message "this client's connection was closed"
        """
        too_many_auth_attempts = C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ERROR + C.MESSAGE_PART_SEPARATOR + "TOO_MANY_AUTH_ATTEMPTS" + C.MESSAGE_SEPARATOR
        Mocket.register(MocketEntry(('localhost', 8989), [str.encode(too_many_auth_attempts)]))
        ds = DeepStreamClient('localhost', 8989)
        credentials = {"username": "XXX", "password": "YYY"}
        ds.login(credentials, None)
        time.sleep(0.1)
        assert ds.get_connection_state() == C.CONNECTION_STATE_AUTHENTICATING
        time.sleep(0.1)
        with pytest.raises(Exception) as excinfo:
            ds.login(credentials, None)
        assert 'client\'s connection was closed' in str(excinfo.value)

    def teardown_method(self, test_method):
        Mocket.reset()

