import logging
import socket

import networking.configuration as config


class MessageHandler:
    def __init__(self, client: socket.socket, name: str):
        super().__init__()
        self.socket = client
        self.prefix = name + ' '
        self.logger = logging.Logger(name)

    def log_message(self, message: str):
        self.logger.info(self.prefix + message)

    def log_warning(self, message: str):
        self.logger.warning(self.prefix + message)

    def receive_message(self):
        header_message = self.socket.recv(config.HEADER_SIZE).decode(config.FORMAT)
        if header_message == '':
            return ''
        try:
            message_length = int(header_message)
        except ValueError as error:
            self.log_warning(f'[Message] [Error] --- {error} ---')
            return ''
        message = self.socket.recv(message_length).decode(config.FORMAT)
        self.logger.info(f'[Message] <<< --- {message} ---')
        return message

    def transmit_message(self, message: str):
        message_length = len(message)
        full_message = f'{message_length:<{config.HEADER_SIZE}}' + message
        self.socket.send(full_message.encode(config.FORMAT))
        self.logger.info(f'[Message] >>> --- {message} ---')
