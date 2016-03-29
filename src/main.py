from src.DeepStreamClient import DeepStreamClient
from tests.feature_tests.test_server import TestServer
from src import Constants as C
import threading
import time

def show(data):
    print(data)


server = TestServer("127.0.0.1", 9999)
server_thread = threading.Thread(target=server.start_listening)
server_thread.setDaemon(True)
server_thread.start()

client = DeepStreamClient("127.0.0.1", 9999)
credentials = {}
credentials["username"] = "XXX"
credentials["password"] = "YYY"
client.login(credentials, None)
time.sleep(1)
msg = server.last_message
auth_msg = C.TOPIC_AUTH + C.MESSAGE_PART_SEPARATOR + C.ACTIONS_REQUEST + C.MESSAGE_PART_SEPARATOR + "{\"password\": \"YYY\", \"username\": \"XXX\"}" + C.MESSAGE_SEPARATOR
assert msg == str.encode(auth_msg)
client._connection.close()