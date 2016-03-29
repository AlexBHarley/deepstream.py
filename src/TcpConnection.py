import socket
from pyee import EventEmitter
from queue import Queue
import threading
import time

class AsyncSocket(threading.Thread):

    def __init__(self, ip, port):
        super(AsyncSocket, self).__init__()
        self.emitter = EventEmitter()
        self.buffer = b''
        self.q = Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((ip, port))
        except:
            time.sleep(0.5)
            self.sock.connect((ip, port))
        self.emitter.emit('open')
        self.timeout = 1
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
                self.sock.sendall(self.buffer)
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
        self.emitter.emit('message', raw_data)

    def _on_close(self):
        self.emitter.emit('close')
        self.join()

    def _close(self):
        self.join()
