import socket
import time

from networking.protocol import PORT, ADDRESS, FORMAT, DISCONNECT_MESSAGE
from networking.logger import Logger


class MessengerSender(Logger):
    def __init__(self):
        super().__init__('[Messenger] ')
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_prefix(f'[{self.name}] ')

    def run(self) -> None:
        self.logging(f'Connecting to port {PORT}')
        self.connect()
        self.send(f'Hello World! from [{self.name}]')
        self.disconnect()

    def disconnect(self):
        time.sleep(1)
        self.send(DISCONNECT_MESSAGE)
        time.sleep(1)
        self.client.close()
        self.logging('Connection closed')

    def connect(self):
        self.client.connect(ADDRESS)

    def send(self, message):
        try:
            self.client.send(message.encode(FORMAT))
        except ConnectionResetError as e:
            self.logging(e)
