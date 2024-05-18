import logging
from threading import Thread


class Logger(Thread):
    def __init__(self, prefix: str):
        super().__init__()
        self.prefix = prefix
        self.logger = logging.getLogger(prefix)

    def set_prefix(self, prefix):
        self.prefix += prefix
        self.logger.name += prefix

    def logging(self, message):
        self.logger.warning(self.prefix + str(message))


class SimpleLogger:
    def __init__(self, prefix: str):
        super().__init__()
        self.prefix = prefix + ' '
        self.logger = logging.Logger(prefix)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def log_debug(self, message: str):
        self.logger.debug(self.prefix + message)

    def log_info(self, message: str):
        self.logger.info(self.prefix + message)

    def log_warning(self, message: str):
        self.logger.warning(self.prefix + message)

    def log_error(self, message: str):
        self.logger.error(self.prefix + message)
