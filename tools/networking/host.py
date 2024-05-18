import socket
import threading
import time
from typing import Dict, Tuple

import select

import networking.protocol as config
from networking.logger import Logger


class ServerHandler(Logger):
    def __init__(self):
        super().__init__('[Server] ')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(config.ADDRESS)
        self.running = threading.Event()
        self.sockets_list = [self.server]
        self.clients_info: Dict[socket.socket, Tuple[str, int]] = {}

    def receive_message(self, client: socket.socket):
        if self.running.is_set() is False:
            self.logging(f'[Connection] [Error] Host server is closing')
            return ''
        message = client.recv(config.HEADER_SIZE).decode(config.FORMAT)
        if message == '':
            return ''
        try:
            message_length = int(message)
        except ValueError as error:
            self.logging(f'[Connection] [Error] Received message --- {message} --- {error} ---')
            return ''
        message = client.recv(message_length).decode(config.FORMAT)
        return message

    def transmit_message(self, client, message):
        message_length = len(message)
        full_message = f'{message_length:<{config.HEADER_SIZE}}' + message
        client.send(full_message.encode(config.FORMAT))
        address = self.clients_info[client][1]
        self.logging(f'[{address}] [Message] >>> --- {message} ---')

    def run(self) -> None:
        self.logging('Starting host server')
        self.server.listen(5)
        self.running.set()
        while self.running.is_set():
            read_sockets, _, _ = select.select(self.sockets_list, [], [], 0.5)
            for notified_socket in read_sockets:
                if notified_socket == self.server:
                    # Accept client socket connection
                    self.accept_client()
                else:
                    # Read client connection message
                    self.read_client(notified_socket)
        for client in self.sockets_list:
            if client == self.server:
                continue
            self.transmit_message(client, config.DISCONNECT_MESSAGE)
            client.close()
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
        if message == config.DISCONNECT_MESSAGE:
            self.close_client(client_socket)

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
