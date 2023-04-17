import random
import tkinter as tk
from multiprocessing import Process, Event
from threading import Event as TEvent

from gui.graph import Graph


class AppProcess(Process):
    def __init__(self):
        super().__init__(name='Tkinter')
        self.stop_event = Event()

    def run(self) -> None:
        app = Application(self.stop_event)
        app.mainloop()
        app.quit()


class Application(tk.Tk):
    def __init__(self, event: TEvent):
        super().__init__()
        self.event = event
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
        self.after(100, lambda: self.poll_running())

    def poll_data(self):
        data_y = self.graph.line.get_ydata()
        data_y += (random.random() * 10 - 1,)
        data_x = self.graph.line.get_xdata()
        data_x += (1 + data_x[-1] if len(data_x) > 0 else 0,)
        self.graph.line.set_ydata(data_y)
        self.graph.line.set_xdata(data_x)
        self.graph.plot.set_xlim(-1, len(data_x) + 1)
        self.graph.draw()
        self.after(100, lambda: self.poll_data())


def main():
    process = AppProcess()
    process.start()
    process.join()


if __name__ == '__main__':
    main()
