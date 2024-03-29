import tkinter as tk

from matplotlib.axes import Axes
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from typing import Dict


class Graph(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        cnf = {'fill': 'both', 'expand': True}

        self.figure: Figure = Figure()
        self.figure.subplots_adjust(0.065, 0.055, 0.985, 0.98)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack_configure(cnf, side='bottom')

        self.toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack_configure(fill='x', side='top')

        self.lines: Dict[str, Line2D] = {}
        self.plot: Axes = self.figure.add_subplot()

    def draw(self):
        if self.winfo_viewable() == 0:
            return
        self.canvas.flush_events()
        self.canvas.draw_idle()

    def create_line(self, key, value=0, point=0):
        if key in self.lines:
            return
        if point is None:
            point = 0
        index = len(self.lines)
        line = Line2D([point], [value], linewidth=1, color=f'C{index}')
        line.set_label(s=key)
        self.plot.add_line(line)
        self.plot.legend(loc='upper right')
        self.lines[key] = line

    def remove_line(self, key):
        line = self.lines.pop(key)
        line.set_label(s=None)
        line.remove()

    def view_line(self, key):
        line = self.lines[key]
        data_y = line.get_ydata()
        data_x = line.get_xdata()
        offset_x = (max(data_x) - min(data_x)) * 0.05 + 1
        offset_y = (max(data_y) - min(data_y)) * 0.05 + 1
        self.plot.set_xlim(min(data_x) - offset_x, max(data_x) + offset_x)
        self.plot.set_ylim(min(data_y) - offset_y, max(data_y) + offset_y)

    def size_line(self, key, size):
        line = self.lines[key]
        if len(line.get_xdata()) < size:
            return
        for line in self.lines.values():
            del line.get_xdata()[:-size // 2]
            del line.get_ydata()[:-size // 2]

    def extend_line(self, key, value, point=None):
        line = self.lines[key]
        data_y = line.get_ydata()
        data_x = line.get_xdata()

        if point is None:
            point = max(data_x) + 1
        data_x += (point,)
        data_y += (value,)
        line.set_ydata(data_y)
        line.set_xdata(data_x)
