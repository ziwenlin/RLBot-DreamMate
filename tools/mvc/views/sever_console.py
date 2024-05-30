import tkinter as tk

from mvc.views.application_window import PADDING_CNF, GRID_CNF


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
