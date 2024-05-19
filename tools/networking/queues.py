from queue import Queue
from typing import List


class SimpleQueue:
    def __init__(self, queue_input=None, queue_output=None):
        if queue_input is None:
            queue_input = Queue()
        if queue_output is None:
            queue_output = Queue()
        self.queue_input = queue_input
        self.queue_output = queue_output

    def connect(self):
        return SimpleQueue(self.queue_output, self.queue_input)

    def put(self, item):
        self.queue_output.put(item)

    def get(self):
        if self.queue_input.empty() is True:
            return None
        return self.queue_input.get()


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
