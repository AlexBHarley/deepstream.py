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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timeout = 0.1

    def run(self):
        try:
            self.sock.connect((self._ip, self._port))
            self._is_open = True
            self.out_q.put(('open', None))
            os.kill(self._main_thread_pid, signal.SIGUSR1)
        except (ConnectionRefusedError, socket.error) as e:
            self._on_error(e)
        self.is_runnning = True
        while True:
            while self.is_runnning:
                try:
                     data = self.in_q.get(timeout=self.timeout)
                     self.buffer += data
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
        self.in_q.put(msg)

    def _on_error(self, e):
        if isinstance(e, socket.error):
            if e.errno == errno.ECONNREFUSED:
                msg = 'Can\'t connect! Deepstream server unreachable'
            else:
                msg = e.strerror
            self._put_err_on_q(msg)
        else:
            self._put_err_on_q(e)

        self.is_runnning = False

    def _put_err_on_q(self, err_msg):
        self.out_q.put(('error', err_msg))
        os.kill(self._main_thread_pid, signal.SIGUSR1)

    def _on_data(self, raw_data):
        if not isinstance(raw_data, bytes):
            self._put_err_on_q('received non-bytes message from socket')
            return

        if not self._is_open:
            self._put_err_on_q('received message on half closed socket: ')
            return

        #todo checks for valid data
        #todo buffer data
        self.out_q.put(('message', raw_data))
        os.kill(self._main_thread_pid, signal.SIGUSR1)
        return

    def _on_close(self):
        self.sock.close()
        self._is_open = False
        self.emitter.emit('close')
