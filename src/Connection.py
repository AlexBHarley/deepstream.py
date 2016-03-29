from src import Constants
from src.message import MessageBuilder
from src.message import MessageParser
from src.TcpConnection import AsyncSocket
from pyee import EventEmitter


class Connection:

    def __init__(self, client, ip_address=None, port=None):
        self._ip_address = ip_address
        self._port = port
        self._auth_params = None
        self._auth_callback = None
        self._deliberate_close = False
        self._too_many_auth_attempts = False
        self.emitter = EventEmitter()
        self.state = Constants.CONNECTION_STATE_CLOSED
        self._client = client
        self._endpoint = None
        self._create_endpoint()

    def authenticate(self, auth_params, callback):
        if self._too_many_auth_attempts:
            self._client._on_error(Constants.TOPIC_ERROR, Constants.EVENT_IS_CLOSED, 'this client\'s connection was closed')
            return
        elif self._deliberate_close == True and self.state == Constants.CONNECTION_STATE_CLOSED:
            self._create_endpoint()
            self._deliberate_close = False
            self._endpoint.emitter.once('open', self.authenticate(self._auth_params, self._auth_callback))

        self._auth_params = auth_params
        self._auth_callback = callback

        if self.state == Constants.CONNECTION_STATE_AWAITING_AUTHENTICATION and self._auth_params != None:
            self._send_auth_params()

    def send_message(self, event, action, data):
        msg = MessageBuilder.get_message(event, action, data)
        self._send(msg)

    def _send(self, data):
        byte_message = str.encode(data)
        self._endpoint.send(byte_message)

    def _send_auth_params(self):
        self.state = Constants.CONNECTION_STATE_AUTHENTICATING
        auth_message = MessageBuilder.get_message(Constants.TOPIC_AUTH, Constants.ACTIONS_REQUEST, [self._auth_params])
        self._send(auth_message)
        self._auth_params = None

    def _handle_auth_response(self, message):
        if message["action"] == Constants.ACTIONS_ERROR:
            if message["data"][0] == Constants.EVENT_TOO_MANY_AUTH_ATTEMPTS:
                self._deliberate_close = True
                self._too_many_auth_attempts = True
            else:
                self.state = Constants.CONNECTION_STATE_AWAITING_AUTHENTICATION

            if self._auth_callback != None:
                self._auth_callback(message)

        elif message["action"] == Constants.ACTIONS_ACK:
            self.state = Constants.CONNECTION_STATE_OPEN

            if self._auth_callback != None:
                self._auth_callback(message["data"][0])

    def _create_endpoint(self):
        self._endpoint = AsyncSocket(self._ip_address, self._port)
        self._endpoint.emitter.on('message', self._on_message)
        self._endpoint.emitter.on('open', self._on_open())
        self._endpoint.start()

    def _on_open(self):
        self.state = Constants.CONNECTION_STATE_AWAITING_AUTHENTICATION
        if self._auth_params != None:
            self._send_auth_params()

    def _on_message(self, message):
        messages = MessageParser.parse(message)
        for msg in messages:
            if msg["topic"] == Constants.TOPIC_AUTH:
                self._handle_auth_response(msg)
            else:
                self._client._on_message(msg)

    def close(self):
        self._endpoint.join(1)
