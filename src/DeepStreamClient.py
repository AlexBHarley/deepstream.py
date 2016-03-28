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

    def login(self, credentials, callback):
        """
        :param credentials: A dict of credentials to authenticate against the server
        :param callback: Callback to be executed upon authentication
        :return: None
        """
        credentials = json.dumps(credentials, sort_keys=True)
        self._connection.authenticate(credentials, callback)

    def get_connection_state(self):
        return self._connection.state

    def _on_message(self, message):
        if message["topic"] == Constants.TOPIC_EVENT:
            self.event.handle(message)

