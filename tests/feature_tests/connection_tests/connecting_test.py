'''
Note: Not sure if this is testable with mocket

Feature: Connecting a client
	As soon as the client is instantiated
	it establishes a TCP connection to the
	server and awaits login
'''


class TestConnectingAClient:

    def test_server_should_have_0_connections(self):
        """
        Scenario: The test server is idle and awaits connections
            Given the test server is ready
            Then the server has 0 active connections
        """
        pass

    def test_when_the_client_is_initialised_server_should_have_an_active_connection(self):
        """
        Scenario: The client is instantiated and creates a tcp connection
            Given the test server is ready
                And the client is initialised
            Then the server has 1 active connections
                And the clients connection state is "AWAITING_AUTHENTICATION"
        """
        pass