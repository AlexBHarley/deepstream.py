import socket, errno
from pyee import EventEmitter
from queue import Queue
import threading
import time


class AsyncSocket(threading.Thread):

    def __init__(self, ip, port):
        super().__init__()
        self._ip = ip
        self._port = port
        self.buffer = b''
        self.q = Queue()
        self.emitter = EventEmitter()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.emitter.emit('open')
        self.timeout = 5
        self.setDaemon(True)

    def _on_thread(self, function, *args, **kwargs):
        '''
        This method and implementation is taken directly from the below stackoverflow link. Allows us to add messages
        to the socket in its own thread.
        http://stackoverflow.com/questions/19033818/how-to-call-a-function-on-a-running-python-thread
        '''
        self.q.put((function, args, kwargs))

    def start(self):
        try:
            self.sock.connect((self._ip, self._port))
        except (ConnectionRefusedError, socket.error) as e:
            self._on_error(e)
        super(AsyncSocket, self).start()

    def run(self):
        while True:
            try:
                function, args, kwargs = self.q.get(timeout=self.timeout)
                function(*args, **kwargs)
            except TimeoutError:
                pass
            except Exception as e:
                self._on_error(e.args)

            if self.buffer != b'':
                sent = self.sock.send(self.buffer)
                if sent == 0:
                    self.emitter.emit('error', 'attempt to send message on closed socket: ' + self.buffer.decode("utf-8"))
                self.buffer = b''

            try:
                data = self.sock.recv(1024)
                if data:
                    self._on_data(data)
            except Exception as e:
                self._on_close()

    def send(self, msg):
        self._on_thread(self._send, msg)

    def _send(self, data):
        self.buffer += data

    def _on_error(self, e):
        if e.errno == errno.ECONNREFUSED:
            msg = 'Can\'t connect! Deepstream server unreachable'
        else:
            msg = e.strerror
        self.emitter.emit('error', msg)

    def _on_data(self, raw_data):
        #todo checks for valid data
        #todo buffer data
        self.emitter.emit('message', raw_data)

    def _on_close(self):
        self.emitter.emit('close')
        self.join()

    def _close(self):
        self.join()
