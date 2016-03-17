Scenario: The client sends login credentials
	Given the client is initialised
	When the client logs in with username "XXX" and password "YYY"
	Then client receives the message A|A+
		And the clients connection state is "AUTHENTICATING"

Scenario: The client receives a login confirmation
	When the server sends the message A|A+
	Then the clients connection state is "OPEN"
		And the last login was successful