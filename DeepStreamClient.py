from Connection import Connection
import json


class DeepStreamClient:

    def __init__(self, ip, port):

        self._connection = Connection(ip, port)

    def login(self, username, password):
        credentials = json.dumps({"username": username, "password": password})
        print("Using credentials %s" % credentials)
        self._connection.authenticate(credentials)
        self._connection._start_message_loop()
