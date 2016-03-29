from src.DeepStreamClient import DeepStreamClient
from tests.feature_tests.test_server import TestServer
from src import Constants as C
import threading
import time

def show(data):
    print(data)


server = TestServer("127.0.0.1", 6767)
server_thread = threading.Thread(target=server.start_listening)
server_thread.setDaemon(True)
server_thread.start()

client = DeepStreamClient("127.0.0.1", 6767)
credentials = {}
credentials["username"] = "user_too_many_auth"
credentials["password"] = "pass_too_many_auth"
client.login(credentials, show)
time.sleep(1)
assert client.get_connection_state() == C.CONNECTION_STATE_AUTHENTICATING
