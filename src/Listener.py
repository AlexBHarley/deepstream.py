from threading import Timer
import src.Constants as C


class Listener:
    def __init__(self, type, pattern, callback, client, connection):
        self._type = type
        self._pattern = pattern
        self._callback = callback
        self._client = client
        self._connection = connection
        self._ack_timeout = Timer(60, self._on_timeout)
        self._ack_timeout.start()
        self._listen()

    def destroy(self):
        self._connection.send_message(self._type, C.ACTIONS_UNLISTEN, [self._pattern])
        self._callback = None
        self._connection = None
        self._pattern = None
        self._client = None

    def _listen(self):
        self._connection.send_message(self._type, C.ACTIONS_LISTEN, [self._pattern])

    def _on_message(self, message):
        if message["action"] == C.ACTIONS_ACK:
            self._ack_timeout.cancel()
        else:
            is_found = message["action"] == C.ACTIONS_SUBSCRIPTION_FOR_PATTERN_FOUND
            self._callback(message["data"][1], is_found)

    def _on_timeout(self):
        self._client._on_error(self._type, C.EVENT_ACK_TIMEOUT, 'No ACK message received in time for ' + self._pattern)
