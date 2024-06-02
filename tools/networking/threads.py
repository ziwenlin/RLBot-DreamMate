import threading

from networking.queues import SimpleQueue


class SimpleThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = threading.Event()
        self.queues = SimpleQueue()

    def start(self) -> None:
        self.running.set()
        super().start()

    def stop(self):
        self.running.clear()
        self.join()
