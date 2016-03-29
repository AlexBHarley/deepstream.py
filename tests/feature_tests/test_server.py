import socket
from src import Constants as C
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
        self.buffer = b''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1)
        self.sock.bind((ip, port))

    def handle_client(self, client):
        self.connection_count += 1
        try:
            data = client.recv(1024)
            if data == str.encode("A" + C.MESSAGE_PART_SEPARATOR + "REQ" + C.MESSAGE_PART_SEPARATOR + "{\"password\": \"pass_too_many_auth\", \"username\": \"user_too_many_auth\"}" + C.MESSAGE_SEPARATOR):
                self.send("A" + C.MESSAGE_PART_SEPARATOR + "E" + C.MESSAGE_PART_SEPARATOR + "TOO_MANY_AUTH_ATTEMPTS" + C.MESSAGE_PART_SEPARATOR + "Stoo many authentication attempts" + C.MESSAGE_SEPARATOR)
            self.last_message = data
            self.all_messages += [data]
        except Exception as e:
            pass

    def start_listening(self):
        self.sock.listen(5)
        self.running = True
        while self.running:
            if self.buffer != b'':
                for c in self.connections:
                    c.send(self.buffer)
                self.buffer = b''
            try:
                client, addr = self.sock.accept()
                self.connections += [client]
                self.handle_client(client)
            except Exception as e:
                pass

    def send(self, msg):
        self.buffer += str.encode(msg)

    def stop(self):
        self.running = False
        for c in self.connections:
            c.close()
        self.sock.close()
