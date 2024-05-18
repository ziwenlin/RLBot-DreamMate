import logging
import socket
import threading
import time
from typing import Dict, Tuple

import select

from networking.client import ClientHandler
from networking.logger import Logger
from networking.protocol import ADDRESS, FORMAT, HEADER_SIZE


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
            self.logging(f'[Connection] [Error] Host server is closing')
            return ''
        message = client.recv(HEADER_SIZE).decode(FORMAT)
        if message == '':
            return ''
        try:
            message_length = int(message)
        except ValueError as error:
            self.logging(f'[Connection] [Error] Received message --- {message} --- {error} ---')
            return ''
        message = client.recv(message_length).decode(FORMAT)
        return message

    def run(self) -> None:
        self.logging('Starting host server')
        self.server.listen(5)
        self.running.set()
        while self.running.is_set():
            read_sockets, _, _ = select.select(self.sockets_list, [], [], 5.0)
            for notified_socket in read_sockets:
                if notified_socket == self.server:
                    # Accept client socket connection
                    self.accept_client()
                else:
                    # Read client connection message
                    self.read_client(notified_socket)
        self.server.close()
        self.logging('Host server closed')

    def accept_client(self):
        # New incoming socket connection
        client, address = self.server.accept()
        self.sockets_list.append(client)
        self.clients_info[client] = address
        self.logging(f'[{address[1]}] [Success] Accepted client handler')

    def read_client(self, client_socket: socket.socket):
        # New incoming message from socket connection
        message = self.receive_message(client_socket)
        address = self.clients_info[client_socket]
        if message is False or message == '':
            # Client have sent an empty message
            self.close_client(client_socket)
            return
        self.logging(f'[{address[1]}] [Message] <<< --- {message} ---')

    def close_client(self, client_socket: socket.socket):
        # Closing client socket connection
        self.sockets_list.remove(client_socket)
        address = self.clients_info[client_socket][1]
        del self.clients_info[client_socket]
        client_socket.close()
        # self.logging(f'Message is false: {message == False}')
        # self.logging(f'Message is empty: {message == ""}')
        self.logging(f'[Connection] Closed client handler at address {address}')

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
    server = ServerHandler()
    server.start()

    client_list = []
    try:
        for _ in range(10):
            client = ClientHandler()
            client.start()
            client_list.append(client)
    except Exception as e:
        logger.warning('[Main] ' + str(e))

    time.sleep(5)
    server.stop()

    for client in client_list:
        while client.is_alive():
            time.sleep(1)
    while server.is_alive():
        time.sleep(1)


if __name__ == '__main__':
    main()
