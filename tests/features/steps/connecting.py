from behave import *
from src.DeepStreamClient import DeepStreamClient
from src import Constants
from tests.features import test_server


@given('the test server is ready')
def step_impl(context):
    context.server = test_server.TestServer('127.0.0.1', 6021)
    context.server.start()
    assert context.server.is_ready

@then('the server has 0 active connections')
def step_impl(context):
    assert len(context.server.connections) == 0

@given('the client is initialised')
def step_impl(context):
    context.client = DeepStreamClient('127.0.0.1', 6021)

    assert (context.conn._ip_address == "127.0.0.1")
    assert (context.conn._port == 6021)

@then('the server has 1 active connections')
def step_impl(context):
    assert len(context.server.connections) == 1

@then('the clients connection state is "AWAITING_AUTHENTICATION"')
def step_impl(context):
    assert (context.client._state == "AWAITING_AUTHENTICATION")


