import socket
from DeepStreamClient import DeepStreamClient
'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 6021))

RECORD_SEPARATOR = '\x1F'
GROUP_SEPARATOR = '\x1E'

msg = str.encode("A" + RECORD_SEPARATOR + "REQ" + RECORD_SEPARATOR + "{\"username\":\"XXX\",\"password\":\"YYY\"}" + GROUP_SEPARATOR, 'utf-8')
print(msg)
s.send(msg)

print(s.recv(1024))
'''
import json
username = "XXX"
password = "YYY"

ds = DeepStreamClient("localhost", 6021)
user = "{\"username\": \"XXX\", \"password\": \"YYY\"}"
ds.login(username, password)
