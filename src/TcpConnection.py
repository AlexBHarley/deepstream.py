from pyee import EventEmitter
from queue import Queue, Empty

import socket, errno
import threading
import signal
import os


class AsyncSocket(threading.Thread):

    def __init__(self, ip, port, pid):
        super().__init__()
        self._ip = ip
        self._port = port
        self._main_thread_pid = pid
        self.buffer = b''
        self.in_q = Queue()
        self.out_q = Queue()
        self._is_open = False
        self.is_runnning = False
        self.emitter = EventEmitter()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timeout = 0.1

    def _on_thread(self, function, *args, **kwargs):
        '''
        This method and implementation is taken directly from the below stackoverflow link. Allows us to add messages
        to the socket in its own thread.
        http://stackoverflow.com/questions/19033818/how-to-call-a-function-on-a-running-python-thread
        '''
        self.in_q.put((function, args, kwargs))

    def start(self):
        try:
            self.sock.connect((self._ip, self._port))
        except (ConnectionRefusedError, socket.error) as e:
            self._on_error(e)
        self._is_open = True
        self.out_q.put({'open'})
        if not self.is_alive():
            super(AsyncSocket, self).start()

    def run(self):
        self.is_runnning = True
        while self.is_runnning:
            try:
                function, args, kwargs = self.in_q.get(timeout=self.timeout)
                function(*args, **kwargs)
            except TimeoutError:
                pass
            except Empty:
                pass
            except Exception as e:
                self._on_error(e.args)

            if self.buffer != b'':
                if self._is_open:
                    try:
                        sent = self.sock.sendall(self.buffer)
                        self.buffer = b''
                    except (ConnectionRefusedError, socket.error) as e:
                        self._on_error(e)
                else:
                    self._on_error("client's connection was closed")

            if self._is_open:
                try:
                    data = self.sock.recv(1024)
                    if data:
                        self._on_data(data)
                except Exception as e:
                    self._on_error(e.args)

    def send(self, msg):
        self._on_thread(self._send, msg)

    def _send(self, data):
        self.buffer += data

    def _on_error(self, e):
        if isinstance(e, socket.error):
            if e.errno == errno.ECONNREFUSED:
                msg = 'Can\'t connect! Deepstream server unreachable'
            else:
                msg = e.strerror
            self.out_q.put({'error': msg})
            os.kill(self._main_thread_pid, signal.SIGUSR1)
        else:
            self.out_q.put({'error': e})
            os.kill(self._main_thread_pid, signal.SIGUSR1)

    def _on_data(self, raw_data):
        if not isinstance(raw_data, bytes):
            self.out_q.put({'error': 'received non-bytes message from socket'})
            os.kill(self._main_thread_pid, signal.SIGUSR1)
            return

        if not self._is_open:
            self.out_q.put({'error': 'received message on half closed socket: ' + raw_data.decode()})
            os.kill(self._main_thread_pid, signal.SIGUSR1)
            return
        #todo checks for valid data
        #todo buffer data
        self.out_q.put({'message': raw_data})
        os.kill(self._main_thread_pid, signal.SIGUSR1)
        return

    def _on_close(self):
        self.sock.close()
        self._is_open = False
        self.emitter.emit('close')
