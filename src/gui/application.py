import random
import threading
import time
import tkinter as tk
from multiprocessing import Process, Queue, Event

from gui.graph import Graph


class AppThread(threading.Thread):
    def __init__(self):
        super().__init__(name='Tkinter')
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


class AppProcess(Process):
    def __init__(self):
        super().__init__(name='Tkinter')
        self.stop_event = Event()
        self.queue_in = Queue()

    def run(self) -> None:
        app = Application(self.stop_event, self.queue_in)
        app.mainloop()
        app.quit()

    def stop(self):
        self.stop_event.set()


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
        value = self.queue_in.get()
        data_y = self.graph.line.get_ydata()
        data_y += (value,)
        data_x = self.graph.line.get_xdata()
        data_x += (1 + data_x[-1] if len(data_x) > 0 else 0,)
        self.graph.line.set_ydata(data_y)
        self.graph.line.set_xdata(data_x)
        self.graph.plot.set_xlim(-1, len(data_x) + 1)
        self.graph.draw()


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
