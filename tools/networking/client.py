import socket
import threading

import select

import networking.configuration as config
from networking.logger import Logger, SimpleLogger
from networking.protocol import MessageHandler


class ClientHandler(threading.Thread):
    def __init__(self):
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        prefix = f'[Client] [{self.name}]'
        self.logger = SimpleLogger(prefix)
        self.messenger = MessageHandler(self.client, prefix)
        self.running = threading.Event()

    def run(self) -> None:
        clients = [self.client]
        self.logger.log_debug('Starting client')
        self.running.set()
        self.connect()
        self.logger.log_info(f'Connected to port {config.PORT}')
        self.messenger.transmit_message(f'Hello World! from [{self.name}]')
        while self.running.is_set():
            readable, _, _ = select.select(clients, [], [], 0.5)
            for notified_socket in readable:
                if notified_socket == self.client:
                    self.read_client()
        self.client.close()
        self.logger.log_debug('Client shutdown')

    def disconnect(self):
        self.messenger.transmit_message(config.DISCONNECT_MESSAGE)
        self.running.clear()
        self.client.close()
        self.logger.log_debug('Connection closed')

    def read_client(self):
        message = self.messenger.receive_message()
        if message is False or message == '':
            self.disconnect()
            return
        if message == config.DISCONNECT_MESSAGE:
            self.disconnect()

    def connect(self):
        self.client.connect(config.ADDRESS)
