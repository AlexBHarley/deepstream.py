import socket
from src import Constants as C
import asyncio
import time
import threading



class TestServer:

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
'''
class DummyServer(asyncio.Protocol):

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

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print(message)
        try:
            pass
            #self.transport.write()
        except:
            pass

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        coro = loop.create_server(DummyServer,
                                  self.ip, self.port)
        server = loop.run_until_complete(coro)
        print("Listening on port {}".format(self.port))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("Shutdown.")
        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()
            print("Exiting")
        return 0
'''
class DummyServer(asyncio.Protocol):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print(message)
        try:
            pass
            #self.transport.write()
        except:
            pass

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        coro = loop.create_server(DummyServer,
                                  self.ip, self.port)
        server = loop.run_until_complete(coro)
        print("Listening on port {}".format(self.port))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("Shutdown.")
        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()
            print("Exiting")
        return 0

