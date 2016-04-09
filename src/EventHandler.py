from src import Constants as C
from pyee import EventEmitter
from src.AckTimeoutRegister import AckTimeoutRegister
from src.Listener import Listener


class EventHandler:

    def __init__(self, connection, client):
        self._connection = connection
        self._emitter = EventEmitter()
        self._client = client
        self._listeners = {}
        self._ack_timeout_register = AckTimeoutRegister(self._client, C.TOPIC_EVENT, 60)

    def handle(self, message):
        name = message["data"][0] if message["action"] is not C.ACTIONS_ACK else message["data"][1]
        if message['action'] == C.ACTIONS_EVENT:
            if len(message['data']) == 2: #ack
                name = message['data'][1]
                self._emitter.emit(name)
            else:
                print('passed, data too short')
                pass

        if name in self._listeners:
            self._listeners[name]._on_message(message)
            return

        if message['action'] == C.ACTIONS_ACK:
            self._ack_timeout_register.clear(message)
            return

    def subscribe(self, event_name, callback):
        self._ack_timeout_register.add(event_name, C.ACTIONS_SUBSCRIBE)
        self._emitter.on(event_name, callback)
        self._connection.send_message(C.TOPIC_EVENT, C.ACTIONS_SUBSCRIBE, [event_name])

    def unsubscribe(self, event_name, callback):
        self._emitter.remove_all_listeners(event_name)
        self._ack_timeout_register.add(event_name, C.ACTIONS_UNSUBSCRIBE)
        self._connection.send_message(C.TOPIC_EVENT, C.ACTIONS_UNSUBSCRIBE, [event_name])

    def listen(self, pattern, callback):
        if pattern in self._listeners:
            self._client._on_error(C.TOPIC_EVENT, C.EVENT_LISTENER_EXISTS, pattern)
        else:
            self._listeners[pattern] = Listener(C.TOPIC_EVENT, pattern, callback, self._client, self._connection)

    def unlisten(self, pattern):
        if pattern in self._listeners:
            self._ack_timeout_register.add(pattern, C.ACTIONS_UNLISTEN)
            #self._listeners[pattern].destroy()
        else:
            self._client._on_error(C.TOPIC_EVENT, C.EVENT_NOT_LISTENING, pattern)


