from src import Constants
from pyee import EventEmitter


class EventHandler:

    _emitter = EventEmitter()

    def __init__(self, connection):
        self._connection = connection
        self._emitter = EventEmitter()

    def subscribe(self, event_name):
        self._connection.send_message(Constants.TOPIC_EVENT, Constants.ACTIONS_SUBSCRIBE, [event_name])

    def handle(self, message):
        if message["data"].length == 2:
            self._emitter.emit(message[0], message[1])
        else:
            pass
