import logging
import socket
import threading
import time
from typing import Dict, Tuple

import select

from networking.client import MessengerSender
from networking.logger import Logger
from networking.protocol import ADDRESS, FORMAT


class ServerHandler(Logger):
    def __init__(self):
        super().__init__('[Server] ')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDRESS)
        self.running = threading.Event()
        self.sockets_list = [self.server]
        self.clients_info: Dict[socket.socket, Tuple[str, int]] = {}

    def receive_message(self, client: socket.socket):
        if self.running.is_set() is False:
            return ''
        message = client.recv(1024).decode(FORMAT)
        return message

    def run(self) -> None:
        self.logging('Starting host server')
        self.server.listen(5)
        self.running.set()
        while self.running.is_set():
            read_sockets, _, _ = select.select(self.sockets_list, [], [], 5.0)
            for notified_socket in read_sockets:
                if notified_socket == self.server:
                    # Client connection accepted
                    client, address = self.server.accept()
                    self.sockets_list.append(client)
                    self.clients_info[client] = address
                    self.logging(f'[Connection] Accepted client handler at address {address[1]}')
                else:
                    message = self.receive_message(notified_socket)
                    address = self.clients_info[notified_socket]
                    if message == False or message == '':
                        # Client connection closed
                        self.sockets_list.remove(notified_socket)
                        del self.clients_info[notified_socket]
                        # self.logging(f'Message is false: {message == False}')
                        # self.logging(f'Message is empty: {message == ""}')
                        self.logging(f'[Connection] Closed client handler at address {address[1]}')
                        continue
                    self.logging(f'[Message] [{address[1]}] > --- {message} ---')
        self.server.close()
        self.logging('Host server closed')

    def stop(self):
        self.logging('Stopping host server')
        self.running.clear()
        for count in range(100):
            # Waiting for host server to close itself
            if self.is_alive():
                time.sleep(0.1)
                continue
            break
        else:
            # Host server did not respond in 10 seconds
            self.logging('Forcing host server to close')
            self.server.close()
        self.logging('Shutdown completed')


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
