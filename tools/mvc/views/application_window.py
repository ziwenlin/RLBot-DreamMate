import tkinter as tk
import tkinter.ttk as ttk

from typing import Dict

from mvc.views.client_console import ClientConsoleView
from mvc.views.server_console import ServerConsoleView
from mvc.views.view_style import GRID_CNF, PADDING_CNF


class ApplicationView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.config(PADDING_CNF)
        self.root.grid_columnconfigure(index=1, weight=1)
        self.root.grid_rowconfigure(index=0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(GRID_CNF, row=0, column=1)

        self.frame = tk.LabelFrame(self.root, text='Settings')
        self.frame.grid(GRID_CNF, row=0, column=0)

        self.label_server_address = tk.Label(self.frame, text='Address')
        self.label_server_address.grid(GRID_CNF, row=0, column=0)

        self.entry_server_address = tk.Entry(self.frame)
        self.entry_server_address.grid(GRID_CNF, row=0, column=1, columnspan=2)

        self.label_server_port = tk.Label(self.frame, text='Port')
        self.label_server_port.grid(GRID_CNF, row=1, column=0)

        self.entry_server_port = tk.Entry(self.frame)
        self.entry_server_port.grid(GRID_CNF, row=1, column=1, columnspan=2)

        self.button_spawn_server = tk.Button(self.frame, text='Spawn Server')
        self.button_spawn_server.grid(GRID_CNF, row=3, column=1)

        self.button_spawn_client = tk.Button(self.frame, text='Spawn Client')
        self.button_spawn_client.grid(GRID_CNF, row=3, column=2)

        self.clients: Dict[str, ClientConsoleView] = {}
        self.servers: Dict[str, ServerConsoleView] = {}

    def remove_server(self, name: str):
        if name not in self.clients:
            print(f'{name} does not exist')
            return
        server = self.servers.pop(name)
        self.notebook.forget(server.frame)
        return server

    def spawn_server(self, name: str):
        if name in self.servers:
            print(f'{name} already exists')
            return
        server = ServerConsoleView(self.notebook)
        self.notebook.add(server.frame, text=name)
        self.servers[name] = server
        return server

    def remove_client(self, name: str):
        if name not in self.clients:
            print(f'{name} does not exist')
            return
        client = self.clients.pop(name)
        self.notebook.forget(client.frame)
        return client

    def spawn_client(self, name: str):
        if name in self.clients:
            print(f'{name} already exists')
            return
        client = ClientConsoleView(self.notebook)
        self.notebook.add(client.frame, text=name)
        self.clients[name] = client
        return client


