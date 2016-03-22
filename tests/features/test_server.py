import socket


class MockServer:
    def __init__(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_ready = False
        self.last_socket = None
        self.connections = []
        self.all_messages = []
        self.last_message = b''
        self.connection_count = 0

    def start(self):
        self.server.bind(("127.0.0.1", 6021))
        self.server.listen(5)
        self.is_ready = True
        while True:
            self.server.accept()
            data = self.server.recv(1024)
            self.last_message = data

    def stop(self):
        self.server.close()
        self.is_ready = False
        self.all_messages = []
        self.last_message = ''
        self.connection_count = 0

    def send(self, message):
        self.last_socket.write(message)

    def bind_socket(self, sock):
        self.connection_count += 1
        self.last_socket = sock
        self.connections.append(sock)

