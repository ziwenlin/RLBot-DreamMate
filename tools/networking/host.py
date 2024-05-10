import logging
import threading
import socket
import time

from typing import Set

from networking.client import MessengerSender
from networking.logger import Logger
from networking.protocol import ADDRESS
from networking.server import ClientHandler


class ServerHandler(Logger):
    def __init__(self):
        super().__init__('[Server] ')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDRESS)
        self.running = threading.Event()
        self.client_lock = threading.Lock()
        self.client_threads: Set[ClientHandler] = set()

    def run(self) -> None:
        self.logging('Starting host server')
        self.server.listen(5)
        while True:
            try:
                client, address = self.server.accept()
            except OSError as e:
                self.logging(e)
                break
            thread = ClientHandler(client, address)
            self.logging(f'Creating client handler {address[1]}')
            with self.client_lock:
                self.client_threads.add(thread)
            thread.start()

    def stop(self):
        self.logging('Stopping host server')
        self.server.close()
        time.sleep(0.01)

        self.logging('Closing client handler connections')
        for thread in self.client_threads:
            if thread.connected is False:
                continue
            self.logging(f'Force closing connection {thread.name}')
            thread.connected = False
            thread.connection.close()
        while len(self.client_threads) > 0:
            thread = self.client_threads.pop()
            if thread.is_alive():
                self.logging(f'Waiting for {thread.name} to finish')
                self.client_threads.add(thread)
        self.logging('Successfully closed all connections')


def main():
    logger = logging.getLogger(__name__)
    logger.info('testing')
    server = ServerHandler()
    server.start()

    try:
        MessengerSender().start()
        MessengerSender().start()
        MessengerSender().start()
        MessengerSender().start()
        MessengerSender().start()
        MessengerSender().start()
        MessengerSender().start()
        MessengerSender().start()
        MessengerSender().start()
    except Exception as e:
        print('[Main] ' + str(e))

    time.sleep(5)
    server.stop()

    while server.is_alive():
        time.sleep(1)


if __name__ == '__main__':
    main()
