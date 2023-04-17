import random
import tkinter as tk
from multiprocessing import Process

from gui.graph import Graph


class ApplicationProcess(Process):
    def run(self) -> None:
        app = ApplicationController()
        app.mainloop()
        app.quit()


class ApplicationController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.frame = tk.Frame(self)
        self.frame.pack(fill='both', expand=True)

        self.graph = Graph(self.frame)
        self.graph.pack(expand=True, fill='both')

        self.graph.plot.set_xlim(-1, 10)
        self.graph.plot.set_ylim(-1, 10)

        self.after(100, lambda: self.poll_data())

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
    app_thread = ApplicationProcess()
    app_thread.start()
    app_thread.join()


if __name__ == '__main__':
    main()
