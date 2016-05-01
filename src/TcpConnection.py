from pyee import EventEmitter
from queue import Queue, Empty

import socket, errno
import threading
import signal
import os


class TcpConnection(EventEmitter):

    def __init__(self, host, port):
        super().__init__()
        self._host = host
        self._port = port
        self.pid = os.getpid()
        self.is_open = False
        signal.signal(signal.SIGUSR1, self._handle_data)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock_thread = SocketThread(self._sock, self)

    def start(self):
        if not self._sock_thread.is_alive():
            self._sock_thread.start()

    def send(self, raw_msg):
        self._sock_thread.in_q.put(raw_msg)

    def connect(self):
        try:
            self._sock.connect((self._host, self._port))
            self.is_open = True
            self.emit('open')
        except ConnectionRefusedError as e:
            self.emit('error', e)

    def _handle_data(self, sig_no, s_frame):
        """
        Method attached to signal, called whenever tcp_connection gets any data. Hands off
        message to the correct _on_* method

        :param sig_no: signal number
        :param s_frame: stack frame
        """
        try:
            msg_type, data = self._sock_thread.out_q.get()
            self.emit(msg_type, data)
        except Empty:
            pass


class SocketThread(threading.Thread):

    def __init__(self, sock, manager):
        super().__init__()
        self._sock = sock
        self._main_thread_pid = manager.pid
        self._manager = manager
        self._buffer = b''
        self.in_q = Queue()
        self.out_q = Queue()
        self.daemon = True

    def run(self):
        while True:
            if self._manager.is_open:
                try:
                    data = self.in_q.get(timeout=0)
                    self._buffer += data
                except (TimeoutError, Empty):
                    pass
                except Exception as e:
                    self._on_error(e.args)

                if self._buffer != b'':
                    try:
                        self._sock.sendall(self._buffer)
                        self._buffer = b''
                    except (ConnectionRefusedError) as e:
                        self._on_error(e)

                try:
                    data = self._sock.recv(1024)
                    if data:
                        self._on_data(data)
                except Exception as e:
                    self._on_error(e.args)

    def _on_error(self, e):
        if isinstance(e, socket.error):
            if e.errno == errno.ECONNREFUSED:
                msg = 'Can\'t connect! Deepstream server unreachable at ' + str(self._manager._host) + ':' + str(self._manager._port)
            else:
                msg = e.strerror
            self._put_err_on_q(msg)
        else:
            self._put_err_on_q(e)

    def _put_err_on_q(self, err_msg):
        self.out_q.put(('error', err_msg))
        os.kill(self._main_thread_pid, signal.SIGUSR1)

    def _on_data(self, raw_data):
        if not isinstance(raw_data, bytes):
            self._put_err_on_q('received non-bytes message from socket')
            return

        #todo checks for valid data
        #todo buffer data
        self.out_q.put(('message', raw_data))
        os.kill(self._main_thread_pid, signal.SIGUSR1)

    def _on_close(self):
        self._sock.close()
        self.out_q.put('close')
