import tkinter as tk
import tkinter.ttk as ttk

from typing import Dict

GRID_CNF = {
    'sticky': tk.NSEW,
}


class ApplicationView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.grid_columnconfigure(index=0, weight=1)
        self.root.grid_rowconfigure(index=0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(GRID_CNF)

        self.server_console = ServerConsoleView(self.notebook)
        self.notebook.add(self.server_console.frame, text='Console')

        self.clients: Dict[str, ClientConsoleView] = {}

    def remove_client(self, name: str):
        if name not in self.clients:
            print(f'{name} does not exist')
            return
        client = self.clients.pop(name)
        self.notebook.forget(client.frame)
        return client

    def create_client(self, name: str):
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
        self.frame = frame = tk.Frame(master)
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

        self.button_spawn_client = tk.Button(frame, text='Spawn client')
        self.button_spawn_client.grid(GRID_CNF, row=0, column=7)

        self.button_disconnect_all = tk.Button(frame, text='Disconnect all')
        self.button_disconnect_all.grid(GRID_CNF, row=0, column=8)

        self.textbox_chat = tk.Text(frame)
        self.textbox_chat.grid(GRID_CNF, columnspan=9)


class ClientConsoleView:
    def __init__(self, master):
        self.master = master
        self.frame = frame = tk.Frame(master)
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

        self.button_disconnect = tk.Button(frame, text='Close')
        self.button_disconnect.grid(GRID_CNF, row=0, column=8)

        self.textbox_chat = tk.Text(frame)
        self.textbox_chat.grid(GRID_CNF, columnspan=9)
