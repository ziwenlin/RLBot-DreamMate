import socket
import threading

from networking.logger import Logger
from networking.protocol import PORT, ADDRESS, FORMAT, DISCONNECT_MESSAGE, HEADER_SIZE


class ClientHandler(Logger):
    def __init__(self):
        super().__init__('[Client] ')
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_prefix(f'[{self.name}] ')
        self.running = threading.Event()

    def run(self) -> None:
        self.logging('Starting client')
        self.running.set()
        self.connect()
        self.logging(f'Connected to port {PORT}')
        self.transmit_message(f'Hello World! from [{self.name}]')
        self.disconnect()
        self.logging('Client shutdown')

    def disconnect(self):
        self.transmit_message(DISCONNECT_MESSAGE)
        self.running.clear()
        self.client.close()
        self.logging('Connection closed')

    def connect(self):
        self.client.connect(ADDRESS)

    def transmit_message(self, message: str):
        if self.running.is_set() is False:
            self.logging(f'[Message] XXX --- {message} ---')
            return
        message_length = len(message)
        full_message = f'{message_length:<{HEADER_SIZE}}' + message
        self.client.send(full_message.encode(FORMAT))
        self.logging(f'[Message] >>> --- {message} ---')
