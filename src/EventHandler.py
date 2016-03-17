from src import Constants
from pyee import EventEmitter


class EventHandler:

    def __init__(self, connection, client):
        self._connection = connection
        self._emitter = EventEmitter()
        self._client = client

    def handle(self, message):
        if message["data"].length == 2:
            self._emitter.emit(message[0], message[1])
        else:
            print('passed, data too short')
            pass

    def subscribe(self, event_name):
        self._connection.send_message(Constants.TOPIC_EVENT, Constants.ACTIONS_SUBSCRIBE, [event_name])
        self._emitter.on(event_name, self.handle)

