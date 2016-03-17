from behave import *
from src.Connection import Connection
import json
from tests.features import test_server

s = test_server.MockServer('127.0.0.1', 6021)
s.start()

@given('the client is initialised')
def step_impl(context):
    context.conn = Connection(None, "127.0.0.1", 6021)

    assert (context.conn._ip_address == "127.0.0.1")
    assert (context.conn._port == 6021)

@when('the client logs in with username "XXX" and password "YYY"')
def step_impl(context):
    credentials = json.dumps({"username": "XXX", "password": "YYY"})
    context.conn.authenicate(credentials)

@then('client receives the message A|A+')
def step_impl(context):
    pass
