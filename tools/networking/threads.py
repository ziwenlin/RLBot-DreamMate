import threading


class SimpleThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = threading.Event()

    def start(self) -> None:
        self.running.set()
        super().start()

    def stop(self):
        self.running.clear()
        self.join()
