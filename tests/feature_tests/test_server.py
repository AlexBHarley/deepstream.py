import socket
import threading
import asyncore


class TestServer(asyncore.dispatcher):

    def __init__(self, ip, port):
        asyncore.dispatcher.__init__(self)
        self.is_ready = True
        self.last_socket = None
        self.connections = []
        self.all_messages = []
        self.last_message = b''
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.set_reuse_addr()
        self.bind((ip, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            try:
                data = sock.recv(1024)
                self.last_message = data
                self.all_messages += data
                self.connections += sock
            except:
                pass


class ServerThread(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.server = TestServer(ip, port)

    def run(self):
        print('Starting run')
        asyncore.loop()

    def stop(self):
        print('Stopping')
        self.server.close()
        self.join()

'''
t = ServerThread('127.0.0.1', 5555)
t.start()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5555))
s.send(b'here i am')
t.stop()'''