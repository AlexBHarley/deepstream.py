import socket
from src import Constants as C
import asyncio
import time
import threading
import ast
import tornado

from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado import gen
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer


class ff:

    def __init__(self, ip, port):
        self.is_ready = True
        self.last_socket = None
        self.running = False
        self.connection_count = 0
        self.connections = []
        self.handle_threads = []
        self.all_messages = []
        self.ip = ip
        self.port = port
        self.last_message = b''
        self.buffer = b''
        self.loop = asyncio.new_event_loop()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1)
        self.sock.bind((ip, port))

    def handle_client(self, client):
        self.connection_count += 1
        while True:
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
                handle_thread = threading.Thread(target=self.handle_client, args=(client,))
                self.handle_threads += [handle_thread]
                handle_thread.setDaemon(True)
                handle_thread.start()
            except Exception as e:
                pass

    def send(self, msg):
        self.buffer += str.encode(msg)

    def stop(self):
        self.running = False
        for c in self.connections:
            c.close()
        for c in self.handle_threads:
            try:
                c.join(1)
            except Exception as e:
                print('here')

        self.sock.close()


class TServer:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection_count = 0
        self.all_messages = []
        self.last_message = b''
        self.loop = asyncio.new_event_loop()
        self.running = True


    @asyncio.coroutine
    def initialise_server(self):
        yield from asyncio.start_server(self.client_connected_handler, self.ip, self.port)

    @asyncio.coroutine
    def client_connected_handler(self, client_reader, client_writer):
        self.connection_count += 1
        while self.running:
            data = yield from asyncio.wait_for(client_reader.read(8192), timeout=0.1)
            if data:
                self.last_message = data
                self.all_messages += [data]
                self.handle(data, client_writer)

    def handle(self, data, client):
        msg = data.decode().split(C.MESSAGE_PART_SEPARATOR)
        if msg[0] == "A":
            auth_data = ast.literal_eval(msg[2].split(C.MESSAGE_SEPARATOR)[0]) #auth_data as {"password": "valid_password", "username": "valid_username"}
            if auth_data['password'] == 'valid_password' and auth_data['username'] == 'valid_username':
                ack = (C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_SEPARATOR)
                client.write(str.encode(ack))
        elif msg[0] == 'E':
            if msg[1] == 'S':
                event_name = msg[2].split(C.MESSAGE_SEPARATOR)[0]
                event_subscribe_ack = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_SUBSCRIBE + C.MESSAGE_PART_SEPARATOR + event_name + C.MESSAGE_SEPARATOR
                client.write(str.encode(event_subscribe_ack))
            if msg[1] == 'US':
                event_name = msg[2].split(C.MESSAGE_SEPARATOR)[0]
                event_unsubscribe_ack = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_UNSUBSCRIBE + C.MESSAGE_PART_SEPARATOR + event_name + C.MESSAGE_SEPARATOR
                client.write(str.encode(event_unsubscribe_ack))
            if msg[1] == C.ACTIONS_LISTEN:
                event_name = msg[2].split(C.MESSAGE_SEPARATOR)[0]
                event_listen_ack = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_LISTEN + C.MESSAGE_PART_SEPARATOR + event_name + C.MESSAGE_SEPARATOR
                client.write(str.encode(event_listen_ack))

    def start(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.initialise_server())
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def stop(self):
        self.running = False

define('port', default=8888, help="TCP port to use")
define('server', default=False, help="Run as the echo server")
define('encoding', default='utf-8', help="String encoding")


class TestServer(TCPServer):
    clients = set()

    def __init__(self):
        super().__init__()
        self.last_message = ''
        self.connection_count = 0
        self.all_messages = []

    @gen.coroutine
    def handle_stream(self, stream, address):
        ip, fileno = address
        print("Incoming connection from " + ip)
        TestServer.clients.add(address)
        while True:
            try:
                yield self.echo(stream)
            except StreamClosedError:
                print("Client " + str(address) + " left.")
                TestServer.clients.remove(address)
                break

    @gen.coroutine
    def echo(self, stream):
        data = yield stream.read_until(C.MESSAGE_SEPARATOR.encode(options.encoding))
        self.last_message = data
        msg = data.decode().split(C.MESSAGE_PART_SEPARATOR)
        ack = ''
        if msg[0] == "A":
            auth_data = ast.literal_eval(msg[2].split(C.MESSAGE_SEPARATOR)[
                                             0])  # auth_data as {"password": "valid_password", "username": "valid_username"}
            if auth_data['password'] == 'valid_password' and auth_data['username'] == 'valid_username':
                ack = (C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_SEPARATOR)
        elif msg[0] == 'E':
            if msg[1] == 'S':
                event_name = msg[2].split(C.MESSAGE_SEPARATOR)[0]
                ack = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_SUBSCRIBE + C.MESSAGE_PART_SEPARATOR + event_name + C.MESSAGE_SEPARATOR
            if msg[1] == 'US':
                event_name = msg[2].split(C.MESSAGE_SEPARATOR)[0]
                ack = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_UNSUBSCRIBE + C.MESSAGE_PART_SEPARATOR + event_name + C.MESSAGE_SEPARATOR
            if msg[1] == C.ACTIONS_LISTEN:
                event_name = msg[2].split(C.MESSAGE_SEPARATOR)[0]
                ack = C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_LISTEN + C.MESSAGE_PART_SEPARATOR + event_name + C.MESSAGE_SEPARATOR
        print('Echoing data: ' + ack)
        yield stream.write(str.encode(ack))

def start_server(test_server):
    server = test_server
    server.listen(options.port, address='127.0.0.1')
    print("Starting server")
    IOLoop.instance().start()

def stop_tornado():
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(ioloop.stop)
    print("Asked Tornado to exit")