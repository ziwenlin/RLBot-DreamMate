import tkinter as tk

from matplotlib.axes import Axes
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class Graph(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.figure: Figure = Figure()

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack_configure()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack_configure()

        self.lines: dict[str, Line2D] = {}
        self.line: Line2D = Line2D([], [], linewidth=1)
        self.plot: Axes = self.figure.add_subplot()
        self.plot.add_line(self.line)

    def draw(self):
        if self.winfo_viewable() == 0:
            return
        self.canvas.flush_events()
        self.canvas.draw_idle()

    def create_line(self, key):
        if key in self.lines:
            return
        index = len(self.lines)
        line = Line2D([], [], linewidth=1, color=f'C{index}')
        self.plot.add_line(line)
        self.lines[key] = line

    def remove_line(self, key):
        line = self.lines.pop(key)
        line.set_label(s=None)
        line.remove()

    def view_line(self, key):
        line = self.lines[key]
        data_y = line.get_ydata()
        data_x = line.get_xdata()
        self.plot.set_xlim(min(data_x) - 1, max(data_x) + 1)
        self.plot.set_ylim(min(data_y) - 1, max(data_y) + 1)

    def extend_line(self, key, value):
        line = self.lines[key]
        data_y = line.get_ydata()
        data_x = line.get_xdata()

        if len(data_x) == 0:
            data_x += (0,)
        else:
            data_x += (1 + data_x[-1],)
        data_y += (value,)
        line.set_ydata(data_y)
        line.set_xdata(data_x)
