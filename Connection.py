import socket

import Constants
from message import MessageBuilder


class Connection:

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, ip_address=None, port=None):

        self._ip_address = ip_address
        self._port = port
        self._auth_params = None

    def open(self):
        self.sock.connect((self._ip_address, self._port))

    def authenticate(self, auth_params):
        self._auth_params = auth_params
        self._send_auth_params()

    def send(self, data):
        byte_message = str.encode(data)
        print("Using bytes: %s" % byte_message)
        self.sock.send(byte_message)
        self._startMessageLoop()

    def start_message_loop(self):
        data = self.sock.recv(1024)
        print("Received %s" % data)

    def _send_auth_params(self):
        auth_message = MessageBuilder.get_message(Constants.TOPIC_AUTH, Constants.ACTIONS_REQUEST, [self._auth_params])
        print("Connecting: %s" % auth_message)
        self.send(auth_message)

