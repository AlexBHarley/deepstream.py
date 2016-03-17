from src.DeepStreamClient import DeepStreamClient

username = "XXX"
password = "YYY"

ds = DeepStreamClient("127.0.0.1", 6021)
ds.login(username, password)

ds.event.subscribe('first_event')