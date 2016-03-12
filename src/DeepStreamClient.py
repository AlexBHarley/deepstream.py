from src.Connection import Connection
from src import Constants
import json
from src.EventHandler import EventHandler


class DeepStreamClient:

    def __init__(self, ip, port):

        self._connection = Connection(ip, port)
        self._event = EventHandler(self._connection)

        self._messageCallbacks = {}
        self._messageCallbacks[Constants.TOPIC_EVENT] = self._event

    def login(self, username, password):
        credentials = json.dumps({"username": username, "password": password})
        print("Using credentials %s" % credentials)
        self._connection.authenticate(credentials)

    def _on_message(self, message):
        if message["topic"] == Constants.TOPIC_EVENT:
            self._event.handle(message)
