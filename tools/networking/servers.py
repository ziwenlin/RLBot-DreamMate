import select
import socket
import threading
from typing import List, Dict, Tuple, Set

from networking import configuration as config
from networking.logger import SimpleLogger
from networking.protocol import MessageProtocolHandler
from networking.queues import SimpleQueue


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.server = ServerSocketHandler(self.name)
        self.running = threading.Event()

    def run(self) -> None:
        self.server.logger.log_debug('Starting host server')
        self.server.start()
        self.running.set()
        while self.running.is_set() is True:
            self.server.main()
        self.server.stop()
        self.server.logger.log_debug('Host server closed')

    def stop(self):
        self.server.logger.log_debug('Stopping host server')
        self.running.clear()
        self.join()
        self.server.logger.log_debug('Shutdown completed')


class ServerSocketHandler:
    def __init__(self, name: str):
        super().__init__()
        self.logger = SimpleLogger(f'[Server] [{name}]')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sockets_list: List[socket.socket] = [self.socket]
        self.clients_dict: Dict[socket.socket, MessageProtocolHandler] = {}
        self.clients_info: Dict[socket.socket, Tuple[str, int]] = {}

    def start(self):
        self.socket.bind(config.ADDRESS)
        self.socket.listen(5)

    def stop(self):
        clients_dict_items = [(a, b) for a, b in self.clients_dict.items()]
        for client_socket, client_protocol in clients_dict_items:
            client_protocol.is_running = False
            client_protocol.process_messages()
            client_socket.close()
        self.socket.close()

    def main(self):
        sockets_list = self.sockets_list
        sockets = select.select(sockets_list, sockets_list, sockets_list, 0.5)
        read_sockets, write_sockets, error_sockets = sockets
        notified_protocols: Set[MessageProtocolHandler] = set()

        # Enable client socket read operation
        for notified_socket in read_sockets:
            if notified_socket == self.socket:
                # Accept client socket connection
                self.accept_client()
                continue
            protocol = self.clients_dict[notified_socket]
            protocol.can_read = True
            notified_protocols.add(protocol)

        # Enable client socket write operation
        for notified_socket in write_sockets:
            if notified_socket == self.socket:
                # Server socket can write?
                self.logger.log_warning('write')
                continue
            protocol = self.clients_dict[notified_socket]
            protocol.can_write = True
            notified_protocols.add(protocol)

        for notified_socket in error_sockets:
            if notified_socket == self.socket:
                self.logger.log_warning('error')
                continue
            protocol = self.clients_dict[notified_socket]
            protocol.has_error = True
            protocol.logger.log_warning('error client')

        # Loop through the notified protocols
        for protocol in notified_protocols:
            if protocol.is_running is True:
                protocol.process_messages()
                continue
            self.close_client(protocol.socket)

    def accept_client(self):
        # Incoming socket connection on the server
        client, address = self.socket.accept()
        name = f'[Server] [P-{address[1]}]'
        queues = SimpleQueue()
        queues.put(f'Hello World! from {name}')
        protocol = MessageProtocolHandler(client, queues, name)
        self.sockets_list.append(client)
        self.clients_info[client] = address
        self.clients_dict[client] = protocol
        self.logger.log_info(f'Accepted client handler at port {address[1]}')

    def close_client(self, client: socket.socket):
        # Closing server socket
        address = self.clients_info.pop(client)
        protocol = self.clients_dict.pop(client)
        protocol.is_running = False
        protocol.process_messages()
        self.sockets_list.remove(client)
        self.logger.log_info(f'Closed client handler at port {address[1]}')
