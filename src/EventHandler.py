from src import Constants
from pyee import EventEmitter


class EventHandler:

    def __init__(self, connection, client):
        self._connection = connection
        self._emitter = EventEmitter()
        self._client = client

    def handle(self, message):
        name = message['data'][1]
        if len(message['data']) == 2:
            self._emitter.emit(name, name)
        else:
            print('passed, data too short')
            pass

    def subscribe(self, event_name, callback):
        self._emitter.on(event_name, callback)
        self._connection.send_message(Constants.TOPIC_EVENT, Constants.ACTIONS_SUBSCRIBE, [event_name])


