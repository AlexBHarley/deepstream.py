from behave import *
from src.DeepStreamClient import DeepStreamClient
from src import Constants
from tests.features import test_server


#background
def background(context):
    context.server = test_server.MockServer('127.0.0.1', 6021)
    context.server.start()

    context.client = DeepStreamClient('127.0.0.1', 6021)

@given('the test server is ready')
def step_impl(context):
    assert context.server.is_ready

@given('the client is initialised')
def step_impl(context):
    assert context.client != None

@when('the client logs in with username "XXX" and password "YYY"')
def step_impl(context):
    context.client.login('XXX', 'YYY')

@then('the last message the server recieved is A|REQ|{"username":"XXX","password":"YYY"}+')
def step_impl(context):
    last_msg = context.server.last_message
    msg = Constants.TOPIC_AUTH + Constants.MESSAGE_PART_SEPARATOR + Constants.ACTIONS_REQUEST + Constants.MESSAGE_PART_SEPARATOR + "{\"username\":\"XXX\",\"password\":\"YYY\"}" + Constants.MESSAGE_SEPARATOR
    assert last_msg == msg

@then('the clients connection state is "AUTHENTICATING"')
def step_impl(context):
    assert context.client.state == Constants.CONNECTION_STATE_AUTHENTICATING
