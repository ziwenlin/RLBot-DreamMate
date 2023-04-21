import random
import threading
import time
import tkinter as tk
from multiprocessing import Process, Queue, Event

from gui.graph import Graph


class AppRunnable:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_event = Event()
        self.queue_in = Queue()

    def send(self, message):
        self.queue_in.put(message)

    def run(self) -> None:
        app = Application(self.stop_event, self.queue_in)
        app.mainloop()
        app.quit()

    def stop(self):
        self.stop_event.set()


class AppThread(AppRunnable, threading.Thread):
    def __init__(self):
        super().__init__(name='Tkinter')


class AppProcess(AppRunnable, Process):
    def __init__(self):
        super().__init__(name='Tkinter')


class Application(tk.Tk):
    def __init__(self, event: threading.Event, queue_in: Queue):
        super().__init__()
        self.event = event
        self.queue_in = queue_in

        self.frame = tk.Frame(self)
        self.frame.pack(fill='both', expand=True)

        self.graph = Graph(self.frame)
        self.graph.pack(expand=True, fill='both')

        self.graph.plot.set_xlim(-1, 10)
        self.graph.plot.set_ylim(-1, 10)

        self.after(100, lambda: self.poll_data())
        self.after(100, lambda: self.poll_running())

    def poll_running(self):
        if self.event.is_set():
            self.quit()
            return
        self.after(100, lambda: self.poll_running())

    def poll_data(self):
        self.after(100, lambda: self.poll_data())
        if self.queue_in.empty():
            return
        while not self.queue_in.empty():
            message = self.queue_in.get()
            self.process_message(message)
        key = next(iter(self.graph.lines.keys()))
        self.graph.view_line(key)
        self.graph.draw()

    def process_message(self, message):
        point = None
        key = 'line'
        if type(message) is str:
            message: str
            data = message.split(':')
            key = data.pop(0)
            value = float(data.pop(0))
            if len(data) > 0:
                point = float(data.pop(0))
        else:
            value = float(message)
        if key not in self.graph.lines:
            self.graph.create_line(key, value=value, point=point - 1)
        self.graph.extend_line(key, value, point)


def main():
    process = AppProcess()
    process.start()

    for _ in range(10):
        time.sleep(0.1)
        process.queue_in.put(random.random() * 10 - 1)

    time.sleep(2)
    process.stop()

    time.sleep(1)
    process.join()


if __name__ == '__main__':
    main()
