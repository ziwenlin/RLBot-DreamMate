import socket
import threading
import time
from typing import Dict, Tuple

import select

import networking.configuration as config
from networking.logger import SimpleLogger
from networking.protocol import MessageHandler


class ServerHandler(threading.Thread):
    def __init__(self):
        super().__init__(name='[Server]')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(config.ADDRESS)
        self.logger = SimpleLogger('[Server]')
        self.running = threading.Event()
        self.sockets_list = [self.server]
        self.clients_handler: Dict[socket.socket, MessageHandler] = {}
        self.clients_info: Dict[socket.socket, Tuple[str, int]] = {}

    def run(self) -> None:
        self.logger.log_debug('Starting host server')
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
            self.clients_handler[client].transmit_message(config.DISCONNECT_MESSAGE)
            client.close()
        self.server.close()
        self.logger.log_debug('Host server closed')

    def accept_client(self):
        # New incoming socket connection
        client, address = self.server.accept()
        self.sockets_list.append(client)
        self.clients_info[client] = address
        self.clients_handler[client] = MessageHandler(client, f'[Server] [{address[1]}]')
        self.logger.log_info(f'[{address[1]}] [Success] Accepted client handler')

    def read_client(self, client_socket: socket.socket):
        # New incoming message from socket connection
        message = self.clients_handler[client_socket].receive_message()
        if message is False or message == '':
            # Client have sent an empty message
            self.close_client(client_socket)
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
        self.logger.log_info(f'[Connection] Closed client handler at address {address}')

    def stop(self):
        self.logger.log_debug('Stopping host server')
        self.running.clear()
        for count in range(100):
            # Waiting for host server to close itself
            if self.is_alive():
                time.sleep(0.1)
                continue
            break
        else:
            # Host server did not respond in 10 seconds
            self.logger.log_debug('Forcing host server to close')
            self.server.close()
        self.logger.log_debug('Shutdown completed')
