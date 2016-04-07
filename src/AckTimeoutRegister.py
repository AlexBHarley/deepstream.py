from pyee import EventEmitter
from threading import Timer
from src import Constants as C

class AckTimeoutRegister:

    def __init__(self, client, topic, timeout_duration):
        self._client = client
        self._topic = topic
        self._timeout_duration = timeout_duration
        self._register = {}
        self._emitter = EventEmitter()

    def add(self, name, action):
        """
        Adds an action to the registry with a timeout. If the timeout happens
        the register emits an error.

        :param name: Name of the occurrence to add to the registry
        :param action: Type of action it is (event etc)
        """
        '''
        unique_name = action + "-" + name if action is not None else name
        '''
        unique_name = name
        if unique_name in self._register:
            self.clear({"data": [unique_name]})
        self._register[unique_name] = Timer(self._timeout_duration, self._on_timeout, args=(unique_name,))
        self._register[unique_name].start()

    def clear(self, event_data):
        name = event_data['data'][1]
        timeout = self._register[name]
        if timeout is not None:
            timeout.cancel()
        else:
            self._client._on_error(self._topic, C.EVENT_UNSOLICITED_MESSAGE, event_data)

    def _on_timeout(self, event_name):
        self._register.pop(event_name)
        msg = 'No ACK message received in time for ' + event_name
        self._client._on_error(self._topic, C.EVENT_ACK_TIMEOUT, msg)
        self._emitter.emit('timeout', event_name)

