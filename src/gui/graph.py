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

        self.line: Line2D = Line2D([], [], linewidth=1)
        self.plot: Axes = self.figure.add_subplot()
        self.plot.add_line(self.line)

    def draw(self):
        if self.winfo_viewable() == 0:
            return
        self.canvas.flush_events()
        self.canvas.draw_idle()
