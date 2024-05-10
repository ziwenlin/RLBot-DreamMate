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
