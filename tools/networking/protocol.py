import socket

import networking.configuration as config
from networking.logger import SimpleLogger
from networking.queues import SimpleQueue


class MessageHandler:
    def __init__(self, client: socket.socket, name: str):
        super().__init__()
        self.socket = client
        self.logger = SimpleLogger(name)

    def receive_message(self):
        header_message = self.socket.recv(config.HEADER_SIZE).decode(config.FORMAT)
        if header_message == '':
            return ''
        try:
            message_length = int(header_message)
        except ValueError as error:
            self.logger.log_warning(f'[Message] [Error] --- {error} ---')
            return ''
        message = self.socket.recv(message_length).decode(config.FORMAT)
        self.logger.log_info(f'[Message] <<< --- {message} ---')
        return message

    def transmit_message(self, message: str):
        message_length = len(message)
        full_message = f'{message_length:<{config.HEADER_SIZE}}' + message
        self.socket.send(full_message.encode(config.FORMAT))
        self.logger.log_info(f'[Message] >>> --- {message} ---')


class MessageProtocolHandler(MessageHandler):
    def __init__(self, client: socket.socket, queues: SimpleQueue, name: str):
        super().__init__(client, name)
        self.can_read = False
        self.can_write = False
        self.has_error = False
        self.is_running = True

        self.queues = queues.connect()

    def _read_message(self):
        self.can_read = False
        message = self.receive_message()
        if message == '' or message == config.DISCONNECT_MESSAGE:
            self.is_running = False
            return
        self.queues.put(message)

    def _write_message(self):
        message = self.queues.get()
        if message is None:
            return
        self.can_write = False
        self.transmit_message(message)

    def process_messages(self):
        if self.is_running is False:
            self.transmit_message(config.DISCONNECT_MESSAGE)
            self.socket.close()
            return
        if self.can_write is True:
            self._write_message()
        if self.can_read is True:
            self._read_message()
