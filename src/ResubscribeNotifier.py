import src.Constants as C


class ResubscribeNotifier:

    def __init__(self, client, resubscribe):
        self._client = client
        self._resubscribe = resubscribe
        self._is_reconnecting = False
        self._client.emitter.on('connection_state_changed', self._connection_state_changed())

    def destroy(self):
        self._client.emitter.remove_listener('connection_state_changed', self._connection_state_changed())
        self._client = None

    def _connection_state_changed(self):
        state = self._client.getConnectionState()

        if state == C.CONNECTION_STATE_RECONNECTING and self._is_reconnecting is False:
            self._is_reconnecting = True

        if state == C.CONNECTION_STATE_OPEN and self._is_reconnecting is True:
            self._is_reconnecting = False
            self._resubscribe()
