import socket
from pyee import EventEmitter
from queue import Queue
import threading
import time


class AsyncSocket(EventEmitter, threading.Thread):

    def __init__(self, ip, port):
        super().__init__()
        self.buffer = b''
        self.q = Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((ip, port))
        except:
            time.sleep(0.5)
            self.sock.connect((ip, port))
        self.emit('open')
        self.timeout = 5
        self.setDaemon(True)

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
                sent = self.sock.send(self.buffer)
                if sent == 0:
                    self.emit('error', 'attempt to send message on closed socket: ' + self.buffer.decode("utf-8"))
                self.buffer = b''

            try:
                data = self.sock.recv(1024)
                if data:
                    self._on_data(data)
            except Exception as e:
                self._on_close()

    def send(self, msg):
        self.onThread(self._send, msg)

    def _send(self, data):
        self.buffer += data

    def _on_data(self, raw_data):
        #todo checks for valid data
        #todo buffer data
        self.emit('message', raw_data)

    def _on_close(self):
        self.emit('close')
        self.join()

    def _close(self):
        self.join()
