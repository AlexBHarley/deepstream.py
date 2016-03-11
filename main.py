from DeepStreamClient import DeepStreamClient

username = "XXX"
password = "YYY"

ds = DeepStreamClient("localhost", 6021)
ds.login(username, password)
