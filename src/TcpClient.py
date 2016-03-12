import socket
from pyee import EventEmitter


class TcpClient(EventEmitter):

    def initialise(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = ip
        self.port = port
        self._open()
        return self

    def send(self, message):
        self.sock.send(message)
        msg = self.sock.recv(1024)
        self.emit("data", msg)

    def _open(self):
        self.sock.connect((self.ip_address, self.port))
        self.on('data', self._on_data)

    def _on_data(self, message):
        self.emit('message', message)

