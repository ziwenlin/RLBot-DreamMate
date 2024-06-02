import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict

from mvc.views.notebook_console import NotebookConsoleView
from mvc.views.view_style import GRID_CNF, PADDING_CNF


class ApplicationView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.config(PADDING_CNF)
        self.root.grid_columnconfigure(index=1, weight=1)
        self.root.grid_rowconfigure(index=0, weight=1)

        self.frame_consoles = tk.LabelFrame(self.root, text='Console')
        self.frame_consoles.grid(GRID_CNF, row=0, column=1)
        self.frame_consoles.grid_rowconfigure(index=0, weight=1)
        self.frame_consoles.grid_columnconfigure(index=0, weight=1)

        self.notebook = ttk.Notebook(self.frame_consoles)
        self.notebook.grid(GRID_CNF)

        self.frame_settings = tk.LabelFrame(self.root, text='Settings')
        self.frame_settings.grid(GRID_CNF, row=0, column=0)

        self.label_server_address = tk.Label(self.frame_settings, text='Address')
        self.label_server_address.grid(GRID_CNF, row=0, column=0)

        self.entry_server_address = tk.Entry(self.frame_settings)
        self.entry_server_address.grid(GRID_CNF, row=0, column=1, columnspan=2)

        self.label_server_port = tk.Label(self.frame_settings, text='Port')
        self.label_server_port.grid(GRID_CNF, row=1, column=0)

        self.entry_server_port = tk.Entry(self.frame_settings)
        self.entry_server_port.grid(GRID_CNF, row=1, column=1, columnspan=2)

        self.button_spawn_server = tk.Button(self.frame_settings, text='Spawn Server')
        self.button_spawn_server.grid(GRID_CNF, row=3, column=1)

        self.button_spawn_client = tk.Button(self.frame_settings, text='Spawn Client')
        self.button_spawn_client.grid(GRID_CNF, row=3, column=2)

        self.consoles: Dict[str, NotebookConsoleView] = {}

    def remove_console(self, name: str):
        if name not in self.consoles:
            print(f'{name} does not exist')
            return
        console = self.consoles.pop(name)
        self.notebook.forget(console.frame)
        return console

    def spawn_console(self, name: str):
        if name in self.consoles:
            print(f'{name} already exists')
            return
        console = NotebookConsoleView(self.notebook)
        self.notebook.add(console.frame, text=name)
        self.consoles[name] = console
        return console

    def append_console(self, name: str, console: NotebookConsoleView):
        if name in self.consoles:
            print(f'{name} already exists')
            return
        self.notebook.add(console.frame, text=name)
        self.consoles[name] = console