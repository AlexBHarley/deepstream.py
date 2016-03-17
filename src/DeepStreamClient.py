from src.Connection import Connection
from src import Constants
import json
from src.EventHandler import EventHandler


class DeepStreamClient:

    def __init__(self, ip, port):
        self._connection = Connection(self, ip, port)

        self.event = EventHandler(self._connection, self)

    def login(self, username, password):
        credentials = json.dumps({"username": username, "password": password})
        self._connection.authenticate(credentials)

    def _on_message(self, message):
        print(message)
        if message["topic"] == Constants.TOPIC_EVENT:
            self.event.handle(message)
