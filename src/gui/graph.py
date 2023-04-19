import tkinter as tk

from matplotlib.axes import Axes
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class Graph(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        cnf = {'fill': 'both', 'expand': True}

        self.figure: Figure = Figure()
        self.figure.subplots_adjust(0.06, 0.05, 0.985, 0.98)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack_configure(cnf)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack_configure(cnf)

        self.lines: dict[str, Line2D] = {}
        self.plot: Axes = self.figure.add_subplot()

    def draw(self):
        if self.winfo_viewable() == 0:
            return
        self.canvas.flush_events()
        self.canvas.draw_idle()

    def create_line(self, key):
        if key in self.lines:
            return
        index = len(self.lines)
        line = Line2D([0], [0], linewidth=1, color=f'C{index}')
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
        self.plot.set_xlim(min(data_x) - 1, max(data_x) + 1)
        self.plot.set_ylim(min(data_y) - 1, max(data_y) + 1)

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
