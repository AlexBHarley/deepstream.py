from src import Constants


def get_message(topic, action, data):
    msg = [topic, action]
    for a in data:
        msg.append(a)
    m = Constants.MESSAGE_PART_SEPARATOR.join(msg) + Constants.MESSAGE_SEPARATOR
    return m
