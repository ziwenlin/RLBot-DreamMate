import tkinter as tk
import tkinter.ttk as ttk

from typing import Dict

GRID_CNF = {
    'sticky': tk.NSEW,
}

PADDING_CNF = {
    'padx': 5, 'pady': 5
}


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


class ServerConsoleView:
    def __init__(self, master):
        self.master = master
        self.frame = frame = tk.LabelFrame(master, PADDING_CNF, text='Console')
        for index in range(9):
            frame.grid_columnconfigure(index=index, weight=1)
        frame.grid_rowconfigure(index=0, weight=0)
        frame.grid_rowconfigure(index=1, weight=1)

        self.entry_message = tk.Entry(frame)
        self.entry_message.grid(GRID_CNF, row=0, column=0, columnspan=3)

        self.button_send_message = tk.Button(frame, text='Send message')
        self.button_send_message.grid(GRID_CNF, row=0, column=3)

        self.button_start_server = tk.Button(frame, text='Start server')
        self.button_start_server.grid(GRID_CNF, row=0, column=4)

        self.button_stop_server = tk.Button(frame, text='Stop server')
        self.button_stop_server.grid(GRID_CNF, row=0, column=5)

        self.button_close_server = tk.Button(frame, text='Close')
        self.button_close_server.grid(GRID_CNF, row=0, column=8)

        self.textbox_chat = tk.Text(frame)
        self.textbox_chat.grid(GRID_CNF, columnspan=9)


class ClientConsoleView:
    def __init__(self, master):
        self.master = master
        self.frame = frame = tk.LabelFrame(master, PADDING_CNF, text='Console')
        for index in range(9):
            frame.grid_columnconfigure(index=index, weight=1)
        frame.grid_rowconfigure(index=0, weight=0)
        frame.grid_rowconfigure(index=1, weight=1)

        self.entry_message = tk.Entry(frame)
        self.entry_message.grid(GRID_CNF, row=0, column=0, columnspan=3)

        self.button_send_message = tk.Button(frame, text='Send message')
        self.button_send_message.grid(GRID_CNF, row=0, column=3)

        self.button_start_server = tk.Button(frame, text='Start client')
        self.button_start_server.grid(GRID_CNF, row=0, column=4)

        self.button_stop_server = tk.Button(frame, text='Stop client')
        self.button_stop_server.grid(GRID_CNF, row=0, column=5)

        self.button_close_client = tk.Button(frame, text='Close')
        self.button_close_client.grid(GRID_CNF, row=0, column=8)

        self.textbox_chat = tk.Text(frame)
        self.textbox_chat.grid(GRID_CNF, columnspan=9)
