import src.Constants as C


def parse(raw_messages, client):
    if type(raw_messages) is bytes:
        raw_messages = raw_messages.decode("utf-8")
    parsed_messages = []
    messages = raw_messages.split(C.MESSAGE_SEPARATOR)
    for msg in messages:
        if len(msg) > 2:
            parsed_messages.append(_parse_message(msg, client))
    return parsed_messages


def _parse_message(message, client):
    tokens = message.split(C.MESSAGE_PART_SEPARATOR)
    message_object = {}
    if len(tokens) < 2:
        client._on_error(C.TOPIC_ERROR, C.EVENT_MESSAGE_PARSE_ERROR, 'Insufficiant message parts')
    if tokens[1] not in C.ACTIONS.values():
        client._on_error(C.TOPIC_ERROR, C.EVENT_MESSAGE_PARSE_ERROR, 'Unknown action ' + tokens[1])
    message_object["topic"] = tokens[0]
    message_object["action"] = tokens[1]
    message_object["data"] = tokens[2:]
    return message_object
