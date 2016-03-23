import socket
import threading


class TestServer(threading.Thread):

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.is_ready = False
        self.last_socket = None
        self.connections = []
        self.all_messages = []
        self.last_message = b''
        super(TestServer, self).__init__()

    def run(self):
        while True:
            self.sock.listen(5)
            self.sock.accept()
            self.is_ready = True
            try:
                data = self.sock.recv(1024)
                if not data:
                    pass
                self._on_data(data)
            except Exception as e:
                pass

    def _on_data(self, raw_data):
        self.last_message = raw_data
        self.all_messages += raw_data

