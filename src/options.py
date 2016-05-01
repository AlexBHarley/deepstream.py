class ClientOptions:
    def __init__(self):

        self.reconnect_interval_increment = 4000
        self.max_reconnect_attempts = 5