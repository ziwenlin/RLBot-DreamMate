import networking.configuration as config


class ApplicationModel:
    def __init__(self):
        self.server_address = str(config.SERVER)
        self.server_port = str(config.PORT)

    def load(self):
        pass

    def save(self):
        pass
