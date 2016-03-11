@connectivity
Feature: Connecting a client
	As soon as the client is instantiated
	it establishes a TCP connection to the
	server and awaits login

Scenario: The client is instantiated and creates a tcp connection
	Given the test server is ready
	Then the client is initialised
	Then the server has 1 active connections
	Then the clients connection state is "AWAITING_AUTHENTICATION"