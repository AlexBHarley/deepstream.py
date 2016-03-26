import socket
import threading


class TestServer:

    def __init__(self, ip, port):
        self.is_ready = True
        self.last_socket = None
        self.running = False
        self.connection_count = 0
        self.connections = []
        self.all_messages = []
        self.ip = ip
        self.port = port
        self.last_message = b''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))

    def handle_client(self, client):
        self.connection_count += 1
        data = client.recv(1024)
        self.last_message = data
        client.close()

    def start_listening(self):
        self.sock.listen(5)
        self.running = True
        while self.running:
            client, addr = self.sock.accept()
            self.handle_client(client)

    def stop(self):
        self.running = False
        self.sock.close()
