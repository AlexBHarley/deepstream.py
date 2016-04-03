from src.DeepStreamClient import DeepStreamClient
from tests.feature_tests.test_server import DummyServer
from src import Constants as C
import time
import socket
import threading


e = DummyServer('127.0.0.1', 6379)
t = threading.Thread(target=e.start)
t.setDaemon(True)
t.start()
time.sleep(1)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('127.0.0.1', 6379))
    s.send(b'hello')
    print(s.recv(1024))
    time.sleep(1)
    s.send(b'hey there')
except Exception as e:
    print(e)
time.sleep(3)
print('End')

'''
client = DeepStreamClient("127.0.0.1", 9999)
credentials = {}
credentials["username"] = "XXX"
credentials["password"] = "YYY"
client.login(credentials, None)
time.sleep(1)
server.send(C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.TOPIC_AUTH + C.MESSAGE_SEPARATOR)
time.sleep(1)
client.event.subscribe("test1", None)
time.sleep(5)
assert server.last_message == str.encode(C.TOPIC_EVENT + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_SUBSCRIBE + C.MESSAGE_PART_SEPARATOR + "test1" + C.MESSAGE_SEPARATOR)
print('hereeeeee')

server.stop()
server_thread.join(1)
'''