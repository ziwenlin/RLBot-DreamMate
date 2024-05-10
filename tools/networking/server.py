import socket

from networking.protocol import FORMAT, DISCONNECT_MESSAGE
from networking.logger import Logger


class ClientHandler(Logger):
    def __init__(self, client, address):
        super().__init__('[Connection] ')
        self.connection: socket.socket = client
        self.address = address
        self.connected = True
        self.set_prefix(f'[{self.name}] ')

    def run(self) -> None:
        self.logging('Connected to ' + str(self.address[1]))
        while self.connected:
            try:
                message = self.connection.recv(1024).decode(FORMAT)
            except ConnectionAbortedError as e:
                self.logging(e)
                break
            if not message:
                break

            if message == DISCONNECT_MESSAGE:
                self.connected = False

            self.logging(f'Message: {message}')
        self.connected = False
        self.connection.close()
        self.logging('Connection closed')
