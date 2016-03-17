from behave import *
from src.Connection import Connection

@given('the test server is ready')
def step_impl(context):
    pass

@then('the client is initialised')
def step_impl(context):
    context.conn = Connection(None, "127.0.0.1", 6021)

    assert (context.conn._ip_address == "127.0.0.1")
    assert (context.conn._port == 6021)

@then('the server has 1 active connections')
def step_impl(context):
    pass

@then('the clients connection state is "AWAITING_AUTHENTICATION"')
def step_impl(context):
    assert (context.conn._state == "AWAITING_AUTHENTICATION")


