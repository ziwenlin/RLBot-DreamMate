import socket
import threading

import select

import networking.configuration as config
from networking.logger import Logger


class ClientHandler(Logger):
    def __init__(self):
        super().__init__('[Client] ')
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_prefix(f'[{self.name}] ')
        self.running = threading.Event()

    def run(self) -> None:
        clients = [self.client]
        self.logging('Starting client')
        self.running.set()
        self.connect()
        self.logging(f'Connected to port {config.PORT}')
        self.transmit_message(f'Hello World! from [{self.name}]')
        while self.running.is_set():
            readable, _, _ = select.select(clients, [], [], 0.5)
            for notified_socket in readable:
                if notified_socket == self.client:
                    self.read_client()
        self.client.close()
        self.logging('Client shutdown')

    def disconnect(self):
        self.transmit_message(config.DISCONNECT_MESSAGE)
        self.running.clear()
        self.client.close()
        self.logging('Connection closed')

    def read_client(self):
        message = self.receive_message()
        if message is False or message == '':
            self.disconnect()
            return
        self.logging(f'[Message] <<< --- {message} ---')
        if message == config.DISCONNECT_MESSAGE:
            self.disconnect()

    def connect(self):
        self.client.connect(config.ADDRESS)

    def receive_message(self):
        if self.running.is_set() is False:
            return ''
        message = self.client.recv(config.HEADER_SIZE).decode(config.FORMAT)
        if message == '':
            return ''
        try:
            message_length = int(message)
        except ValueError as error:
            self.logging(f'[Message] [Error] --- {error} ---')
            return ''
        message = self.client.recv(message_length).decode(config.FORMAT)
        return message

    def transmit_message(self, message: str):
        if self.running.is_set() is False:
            self.logging(f'[Message] XXX --- {message} ---')
            return
        message_length = len(message)
        full_message = f'{message_length:<{config.HEADER_SIZE}}' + message
        self.client.send(full_message.encode(config.FORMAT))
        self.logging(f'[Message] >>> --- {message} ---')
