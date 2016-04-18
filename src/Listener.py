from threading import Timer
from src.ResubscribeNotifier import ResubscribeNotifier
import src.Constants as C


class Listener:
    def __init__(self, topic, pattern, callback, client, connection):
        self._topic = topic
        self._pattern = pattern
        self._callback = callback
        self._client = client
        self._connection = connection
        self._ack_timeout = Timer(10, self._on_timeout)
        self._ack_timeout.start()
        self._resubscribe_notifier = ResubscribeNotifier(self._client, self._listen())
        self._listen()

    def destroy(self):
        self._connection.send_message(self._topic, C.ACTIONS_UNLISTEN, [self._pattern])
        self._resubscribe_notifier.destroy()
        self._callback = None
        self._connection = None
        self._pattern = None
        self._client = None

    def _listen(self):
        self._connection.send_message(self._topic, C.ACTIONS_LISTEN, [self._pattern])

    def _on_message(self, message):
        if message["action"] == C.ACTIONS_ACK:
            self._ack_timeout.cancel()
        else:
            is_found = message["action"] == C.ACTIONS_SUBSCRIPTION_FOR_PATTERN_FOUND
            self._callback(message["data"][1], is_found)

    def _on_timeout(self):
        self._client._on_error(self._topic, C.EVENT_ACK_TIMEOUT, 'No ACK message received in time for ' + self._pattern)
