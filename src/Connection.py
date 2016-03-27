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
        self.emitter = EventEmitter()
        self.state = Constants.CONNECTION_STATE_CLOSED
        self._client = client
        self._endpoint = None
        self._create_endpoint()
        self.state = Constants.CONNECTION_STATE_AWAITING_AUTHENTICATION

    def authenticate(self, auth_params):
        self._auth_params = auth_params
        self.state = Constants.CONNECTION_STATE_AUTHENTICATING
        self._send_auth_params()

    def send_message(self, event, action, data):
        msg = MessageBuilder.get_message(event, action, data)
        self._send(msg)

    def _send(self, data):
        byte_message = str.encode(data)
        self._endpoint.send(byte_message)

    def _send_auth_params(self):
        auth_message = MessageBuilder.get_message(Constants.TOPIC_AUTH, Constants.ACTIONS_REQUEST, [self._auth_params])
        self._send(auth_message)

    def _handle_auth_response(self, message):
        if message["action"] == Constants.ACTIONS_ACK:
            self.state = Constants.CONNECTION_STATE_OPEN

    def _create_endpoint(self):
        self._endpoint = AsyncSocket(self._ip_address, self._port)
        self._endpoint.emitter.on('message', self._on_message)
        self._endpoint.start()

    def _on_message(self, message):
        messages = MessageParser.parse(message)
        for msg in messages:
            if msg["topic"] == Constants.TOPIC_AUTH:
                self._handle_auth_response(msg)
            else:
                self._client._on_message(msg)

    def close(self):
        print('Closing')
        self._endpoint.join(1)
        print(self._endpoint.is_alive())
