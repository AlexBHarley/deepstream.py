from behave import *

@given('the test server is ready')
def step_impl(context):
    pass


@then('the client is initialised')
def step_impl(context):
    context.ds = Connection("localhost", 6021)
    assert (context.ds != None)


@then('the server has 1 active connections')
def step_impl(context):
    pass

@then('the clients connection state is "AWAITING_AUTHENTICATION"')
def step_impl(context):
    assert (context.ds._state == "AWAITING_AUTHENTICATION")
