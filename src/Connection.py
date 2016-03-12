import socket
from src import Constants
from src.message import MessageBuilder


class Connection:

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, ip_address=None, port=None):

        self._ip_address = ip_address
        self._port = port
        self._auth_params = None
        self._state = Constants.CONNECTION_STATE_CLOSED

    def _open(self):
        self.sock.connect((self._ip_address, self._port))
        self._state = Constants.CONNECTION_STATE_AWAITING_AUTHENTICATION

    def authenticate(self, auth_params):
        self._open()
        self._auth_params = auth_params
        self._state = Constants.CONNECTION_STATE_AUTHENTICATING
        self._send_auth_params()

    def send(self, data):
        byte_message = str.encode(data)
        print("Using bytes: %s" % byte_message)
        self.sock.send(byte_message)
        self._start_message_loop()

    def _start_message_loop(self):
        data = self.sock.recv(1024)
        messages = MessageParser.parse(data)

        for msg in messages:
            if msg["topic"] == Constants.TOPIC_AUTH:
                self._handle_auth_response(msg)

    def _send_auth_params(self):
        auth_message = MessageBuilder.get_message(Constants.TOPIC_AUTH, Constants.ACTIONS_REQUEST, [self._auth_params])
        print("Connecting: %s" % auth_message)
        self.send(auth_message)

    def _handle_auth_response(self, message):
        Constants.CONNECTION_STATE_OPEN
