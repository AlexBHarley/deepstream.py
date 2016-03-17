import socket
from pyee import EventEmitter
from queue import Queue
import threading


class AsyncSocket(threading.Thread):

    def __init__(self, ip, port):
        self.buffer = b''
        self.q = Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.timeout = 1
        self._emitter = EventEmitter()
        super(AsyncSocket, self).__init__()

    def onThread(self, function, *args, **kwargs):
        self.q.put((function, args, kwargs))

    def run(self):
        while True:
            try:
                function, args, kwargs = self.q.get(timeout=self.timeout)
                function(*args, **kwargs)
            except:
                pass

            if self.buffer != b'':
                self.sock.sendall(self.buffer)
                self.buffer = b''

            try:
                data = self.sock.recv(1024)
                if not data:
                    pass
                self._emitter.emit('data', data)
            except Exception as e:
                pass

    def send(self, msg):
        self.onThread(self._send, msg)

    def _send(self, data):
        self.buffer += data
