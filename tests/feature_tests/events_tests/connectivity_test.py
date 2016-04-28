from src.DeepStreamClient import DeepStreamClient
from src import Constants as C
from mocket.mocket import Mocketizer, Mocket, MocketEntry

import time
import unittest

"""
Feature: Events Connectivity
	Events subscriptions must be resent to the server after connection
	issues to guarantee it continues recieving them correctly. This
	applies to both subscribing to events and listening to event
	subscriptions.
"""


class TestEventConnection(unittest.TestCase):
    @Mocketizer.wrap
    def test_client_subscribes_to_event(self):
        """
        Scenario: The client subscribes to an event
            Given the client subscribes to an event named "test1"
            Then the last message the server received is E|S|test1+
        	Then the server sends the message E|A|S|test1+
        """
        ack = C.ACTIONS_ACK + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ACK + C.MESSAGE_SEPARATOR
        subscribe_ack = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ACK + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_SUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR
        subscribe = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_SUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR
        Mocket.register(MocketEntry(('localhost', 8989), [str.encode(ack), str.encode(subscribe_ack)]))
        ds = DeepStreamClient('localhost', 8989)
        ds.login({"username": "XXX", "password": "YYY"}, None)
        time.sleep(0.1)
        ds.event.subscribe("test1", None)
        time.sleep(0.1)
        assert Mocket.last_request() == (str(str.encode(subscribe)))

    @Mocketizer.wrap
    def test_client_unsubscribes_to_event(self):

        ack = C.ACTIONS_ACK + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ACK + C.MESSAGE_SEPARATOR
        unsubscribe_ack = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ACK + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_UNSUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR
        unsubscribe = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_UNSUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR
        Mocket.register(MocketEntry(('localhost', 8989), [str.encode(ack), str.encode(unsubscribe_ack)]))
        ds = DeepStreamClient('localhost', 8989)
        ds.login({"username": "XXX", "password": "YYY"}, None)
        time.sleep(0.1)
        ds.event.unsubscribe("test1", None)
        time.sleep(0.1)
        assert Mocket.last_request() == (str(str.encode(unsubscribe)))

    @Mocketizer.wrap
    def test_client_listens_to_event_prefix(self):
        '''
        Scenario: The client listens to eventPrefix
            When the client listens to events matching "eventPrefix/.*"
            Then the last message the server received is E|L|eventPrefix/.*+
            Then the server sends the message E|A|L|eventPrefix/.*+
        '''
        ack = C.ACTIONS_ACK + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ACK + C.MESSAGE_SEPARATOR
        listen_ack = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ACK + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_LISTEN + C.MESSAGE_PART_SEPARATOR + "regex/\*" + C.MESSAGE_SEPARATOR
        listen = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_LISTEN + C.MESSAGE_PART_SEPARATOR + "regex/\*" + C.MESSAGE_SEPARATOR
        Mocket.register(MocketEntry(('localhost', 8989), [str.encode(ack), str.encode(listen_ack)]))
        ds = DeepStreamClient('localhost', 8989)
        ds.login({"username": "XXX", "password": "YYY"}, None)
        time.sleep(0.1)
        ds.event.listen("regex/\*", None)
        time.sleep(0.1)
        assert Mocket.last_request() == (str(str.encode(listen)))

    @Mocketizer.wrap
    def test_client_throws_error_when_connection_lost(self):
        """
        Scenario: The client loses its connection to the server
            When the connection to the server is lost
            Given two seconds later
            Then the client throws a "connectionError" error with message "Can't connect! Deepstream server unreachable"
                And the clients connection state is "RECONNECTING"
        """
        ack = C.ACTIONS_ACK + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_ACK + C.MESSAGE_SEPARATOR
        Mocket.register(MocketEntry(('localhost', 8989), [str.encode(ack)]))
        ds = DeepStreamClient('localhost', 8989)
        ds.login({"username": "XXX", "password": "YYY"}, None)
        time.sleep(1)
        Mocket.reset()
        time.sleep(1)

        with self.assertRaises(Exception) as c:
            ds.event.subscribe('event1', None)
            time.sleep(2)
        self.assertTrue("Can't connect! Deepstream server unreachable" in c.exception.args[0])

    def teardown_method(self, test_method):
        Mocket.reset()



'''
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
	Then the server received the message E|EVT|test1|SyetAnotherValue+
'''
