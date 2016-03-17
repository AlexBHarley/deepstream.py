from src import Constants


def parse(message):
    parsed_messages = []
    raw_messages = message.decode("utf-8").split(Constants.MESSAGE_SEPARATOR)
    for raw in raw_messages:
        if(len(raw) > 2):
            parsed_messages.append(_parse_message(raw))

    return parsed_messages


def _parse_message(message):
    parts = message.split(Constants.MESSAGE_PART_SEPARATOR)
    message_object = {}

    message_object["topic"] = parts[0]
    message_object["action"] = parts[1]
    message_object["data"] = parts[2:]

    return message_object
