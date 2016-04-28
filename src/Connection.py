from src import Constants
from src.message import MessageBuilder
from src.message import MessageParser
from src.TcpConnection import AsyncSocket

from queue import Empty

import signal
import os


class Connection:

    def __init__(self, client, ip_address=None, port=None):
        self._ip_address = ip_address
        self._port = port
        self._auth_params = None
        self._auth_callback = None
        self._deliberate_close = False
        self._too_many_auth_attempts = False
        self.state = Constants.CONNECTION_STATE_CLOSED
        signal.signal(signal.SIGUSR1, self._handle_data)
        self._pid = os.getpid()
        self._client = client
        self._endpoint = None
        self._reconnection_attempt = 0
        self._reconnect_attempts = 5
        self._create_endpoint()

    def authenticate(self, auth_params, callback):
        if self._too_many_auth_attempts:
            self._client._on_error(Constants.TOPIC_ERROR, Constants.EVENT_IS_CLOSED, 'this client\'s connection was closed')
            return
        elif self._deliberate_close is True and self.state == Constants.CONNECTION_STATE_CLOSED:
            self._create_endpoint()
            self._deliberate_close = False
            self._endpoint.once('open', self.authenticate(self._auth_params, self._auth_callback))

        self._auth_params = auth_params
        self._auth_callback = callback

        if self.state == Constants.CONNECTION_STATE_AWAITING_AUTHENTICATION and self._auth_params is not None:
            self._send_auth_params()

    def send_message(self, topic, action, data):
        """
        High level send action for the connection

        :param topic: {string} one of C.TOPIC_*
        :param action: {string} one of C.ACTION_*
        :param data: {[]} the data to be added to the message
        """
        msg = MessageBuilder.get_message(topic, action, data)
        self._send(msg)

    def _send(self, data):
        """
        Class private send method

        :param data: {string} data to be sent
        """
        byte_message = str.encode(data)
        self._endpoint.send(byte_message)

    def _send_auth_params(self):
        """
        Class private method for sending authentication parameters. Values taken
        from self._auth_params
        """
        self._set_state(Constants.CONNECTION_STATE_AUTHENTICATING)
        auth_message = MessageBuilder.get_message(Constants.TOPIC_AUTH, Constants.ACTIONS_REQUEST, [self._auth_params])
        self._send(auth_message)
        self._auth_params = None

    def _handle_auth_response(self, message):
        """
        Method for handling any auth
        :param message:
        :return:
        """
        if message["action"] == Constants.ACTIONS_ERROR:
            if message["data"][0] == Constants.EVENT_TOO_MANY_AUTH_ATTEMPTS:
                self._deliberate_close = True
                self._too_many_auth_attempts = True
            else:
                self._set_state(Constants.CONNECTION_STATE_AWAITING_AUTHENTICATION)

            if self._auth_callback is not None:
                self._auth_callback(False, message["data"][0], message["data"][1])

        elif message["action"] == Constants.ACTIONS_ACK:
            self._set_state(Constants.CONNECTION_STATE_OPEN)

            if self._auth_callback is not None:
                self._auth_callback(True, None, None)

    def _create_endpoint(self):
        self._endpoint = AsyncSocket(self._ip_address, self._port, self._pid)
        self._endpoint.start()

    def _handle_data(self, sig_no, s_frame):
        """
        Method attached to signal, called whenever tcp_connection gets any data. Hands off
        message to the correct _on_* method

        :param sig_no: signal number
        :param s_frame: stack frame
        """
        try:
            msg_type, data = self._endpoint.out_q.get()

            if msg_type == 'open':
                self._on_open()
            elif msg_type == 'message':
                self._on_message(data)
            elif msg_type == 'error':
                self._on_error(data)
            elif msg_type == 'close':
                self._on_close()
        except Empty:
            pass

    def _on_open(self):
        """
        Method called when tcp_connection opens. Sets state and sends authentication
        parameters
        """
        self._set_state(Constants.CONNECTION_STATE_AWAITING_AUTHENTICATION)
        if self._auth_params is not None:
            self._send_auth_params()

    def _on_message(self, message):
        """
        Method for handling incoming data from tcp_connection. Takes care of auth, otherwise
        passes up to the client

        :param message: {string} message to be parsed and handled
        """
        messages = MessageParser.parse(message, self._client)
        for msg in messages:
            if msg["topic"] == Constants.TOPIC_AUTH:
                self._handle_auth_response(msg)
            else:
                self._client._on_message(msg)

    def _on_error(self, message):
        """
        Method for handling errors. Sets the connection state to error and passes
        error up to the client

        :param message: {string} the error message
        """
        self._set_state(Constants.CONNECTION_STATE_ERROR)
        self._client._on_error(None, Constants.CONNECTION_STATE_ERROR, message)

    def _on_close(self):
        if self._deliberate_close is True:
            self.state = Constants.CONNECTION_STATE_CLOSED
        else:
            self._try_reconnect()

    def _try_reconnect(self):
        self._set_state(Constants.CONNECTION_STATE_RECONNECTING)
        if self._reconnection_attempt < self._reconnect_attempts:
            self._try_open()
        self._reconnection_attempt += 1

    def _try_open(self):
        self._endpoint.start()

    def _set_state(self, state):
        """
        Sets the connection state and emits a con_state_changed string to the
        client

        :param state: {string} specific state to change to
        """
        self.state = state
        self._client.emitter.emit(Constants.EVENT_CONNECTION_STATE_CHANGED, state)