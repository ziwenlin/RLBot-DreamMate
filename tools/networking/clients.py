import socket
from typing import List, Dict, Set

import select

from networking import configuration as config
from networking.logger import SimpleLogger
from networking.protocol import MessageProtocolHandler
from networking.queues import SimpleQueue
from networking.threads import SimpleThread


class ClientThread(SimpleThread):
    def __init__(self):
        super().__init__()
        self.client = ClientSocketHandler(self.name, self.queues)

    def run(self) -> None:
        self.client.logger.log_debug('Starting client server')
        self.client.start()
        self.client.logger.log_info(f'Connected to port {config.PORT}')
        while self.running.is_set() is True:
            self.client.main()
        self.client.stop()
        self.client.logger.log_debug('Client server closed')

    def stop(self):
        self.client.logger.log_debug('Stopping client server')
        super().stop()
        self.client.logger.log_debug('Client shutdown completed')


class ClientSocketHandler:
    def __init__(self, name: str, queues: SimpleQueue):
        super().__init__()
        self.queues = queues.connect()
        self.name = f'[Client] [{name}]'
        self.logger = SimpleLogger(self.name)

        self.sockets_list: List[socket.socket] = []
        self.queues_dict: Dict[socket.socket, SimpleQueue] = {}
        self.protocol_dict: Dict[socket.socket, MessageProtocolHandler] = {}

    def start(self):
        self.connect_client()
        client = self.sockets_list[0]
        queues = self.queues_dict[client]
        queues.put(f'Hello World! from {self.name}')

    def stop(self):
        clients_dict_items = [(a, b) for a, b in self.protocol_dict.items()]
        for client_socket, protocol_queues in self.queues_dict.items():
            protocol_queues.put(config.DISCONNECT_MESSAGE)
        for client_socket, client_protocol in clients_dict_items:
            client_protocol.process_messages()
            client_socket.close()
        self.logger.log_debug('Connection closed')

    def main(self):
        sockets_list = self.sockets_list
        sockets = select.select(sockets_list, sockets_list, sockets_list, 0.5)
        read_sockets, write_sockets, error_sockets = sockets
        notified_protocols: Set[MessageProtocolHandler] = set()

        # Read queue messages from other thread into protocol queues
        messages = []
        message_out = self.queues.get()
        while message_out is not None:
            messages.append(message_out)
            message_out = self.queues.get()

        # Read and write messages from protocol queues
        for queues in self.queues_dict.values():
            message_in = queues.get()
            while message_in is not None:
                self.queues.put(message_in)
                message_in = queues.get()
            for message_out in messages:
                queues.put(message_out)

        # Enable client socket read operation
        for notified_socket in read_sockets:
            protocol = self.protocol_dict[notified_socket]
            protocol.can_read = True
            notified_protocols.add(protocol)

        # Enable client socket write operation
        for notified_socket in write_sockets:
            protocol = self.protocol_dict[notified_socket]
            protocol.can_write = True
            notified_protocols.add(protocol)

        for notified_socket in error_sockets:
            protocol = self.protocol_dict[notified_socket]
            protocol.has_error = True
            protocol.logger.log_warning('error client')

        # Loop through the notified protocols
        for protocol in notified_protocols:
            if protocol.is_running is True:
                protocol.process_messages()
                continue
            self.close_client(protocol.socket)

    def connect_client(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(config.ADDRESS)
        queues = SimpleQueue()
        protocol = MessageProtocolHandler(client, queues, self.name)
        self.sockets_list.append(client)
        self.queues_dict[client] = queues
        self.protocol_dict[client] = protocol
        self.logger.log_debug(f'Connected to port {config.PORT}')

    def close_client(self, client: socket.socket):
        protocol = self.protocol_dict.pop(client)
        protocol.is_running = False
        protocol.process_messages()
        self.sockets_list.remove(client)
        self.logger.log_info(f'Closed client handler')
