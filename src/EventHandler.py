from src import Constants as C
from pyee import EventEmitter
from src.AckTimeoutRegister import AckTimeoutRegister

class EventHandler:

    def __init__(self, connection, client):
        self._connection = connection
        self._emitter = EventEmitter()
        self._client = client
        self._ack_timeout_register = AckTimeoutRegister(self._client, C.TOPIC_EVENT, 60)

    def handle(self, message):
        if message['action'] == C.ACTIONS_ACK:
            self._ack_timeout_register.clear(message)

        if len(message['data']) == 2: #ack
            name = message['data'][1]
            self._emitter.emit(name)
        else:
            print('passed, data too short')
            pass

    def subscribe(self, event_name, callback):
        self._ack_timeout_register.add(event_name, C.ACTIONS_SUBSCRIBE)
        self._emitter.on(event_name, callback)
        self._connection.send_message(C.TOPIC_EVENT, C.ACTIONS_SUBSCRIBE, [event_name])

    def unsubscribe(self, event_name, callback):
        self._emitter.remove_all_listeners(event_name)
        self._ack_timeout_register.add(event_name, C.ACTIONS_UNSUBSCRIBE)
        self._connection.send_message(C.TOPIC_EVENT, C.ACTIONS_UNSUBSCRIBE, [event_name])

