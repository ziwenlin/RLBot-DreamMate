import socket
from queue import Queue
from typing import List

import networking.configuration as config
from networking.logger import SimpleLogger


class MultiQueue:
    def __init__(self):
        self.queue_input: List[Queue] = []
        self.queue_output: List[Queue] = []

    def create_output_queue(self):
        queue = Queue()
        self.queue_output.append(queue)
        return queue

    def create_input_queue(self):
        queue = Queue()
        self.queue_input.append(queue)
        return queue

    # def remove_output_queue(self, queue: Queue):
    #     self.queue_output.remove(queue)
    #
    # def remove_input_queue(self, queue: Queue):
    #     self.queue_input.remove(queue)

    def put(self, item):
        for queue in self.queue_output:
            queue.put(item)

    def get(self):
        items = []
        for queue in self.queue_input:
            if queue.empty():
                continue
            items.append(queue.get())
        return items


class MessageHandler:
    def __init__(self, client: socket.socket, name: str):
        super().__init__()
        self.socket = client
        self.logger = SimpleLogger(name)

    def receive_message(self):
        header_message = self.socket.recv(config.HEADER_SIZE).decode(config.FORMAT)
        if header_message == '':
            return ''
        try:
            message_length = int(header_message)
        except ValueError as error:
            self.logger.log_warning(f'[Message] [Error] --- {error} ---')
            return ''
        message = self.socket.recv(message_length).decode(config.FORMAT)
        self.logger.log_info(f'[Message] <<< --- {message} ---')
        return message

    def transmit_message(self, message: str):
        message_length = len(message)
        full_message = f'{message_length:<{config.HEADER_SIZE}}' + message
        self.socket.send(full_message.encode(config.FORMAT))
        self.logger.log_info(f'[Message] >>> --- {message} ---')
