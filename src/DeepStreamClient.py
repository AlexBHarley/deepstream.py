from src.Connection import Connection
from src import Constants
import json
from src.EventHandler import EventHandler


class DeepStreamClient:

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._connection = Connection(self, self._ip, self._port)

        self.event = EventHandler(self._connection, self)

    def login(self, username, password):
        credentials = json.dumps({"username": username, "password": password})
        self._connection.authenticate(credentials)

    def get_connection_state(self):
        return self._connection.state

    def _on_message(self, message):
        if message["topic"] == Constants.TOPIC_EVENT:
            self.event.handle(message)

