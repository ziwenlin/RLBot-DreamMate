import tkinter as tk

from mvc.views.view_style import PADDING_CNF, GRID_CNF


class NotebookConsoleView:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(master)
        self.frame.grid_rowconfigure(index=0, weight=0)
        self.frame.grid_rowconfigure(index=1, weight=1)
        self.frame.grid_columnconfigure(index=0, weight=1)

        self.frame_control = tk.LabelFrame(self.frame, PADDING_CNF, text='Controls')
        self.frame_control.grid(GRID_CNF)
        for index in range(9):
            self.frame_control.grid_columnconfigure(index=index, weight=1)
        self.frame_control.grid_rowconfigure(index=0, weight=0)

        self.entry_message = tk.Entry(self.frame_control)
        self.entry_message.grid(GRID_CNF, row=0, column=0, columnspan=3)

        self.button_send = tk.Button(self.frame_control, text='Send')
        self.button_send.grid(GRID_CNF, row=0, column=3)

        self.button_start = tk.Button(self.frame_control, text='Start')
        self.button_start.grid(GRID_CNF, row=0, column=4)

        self.button_stop = tk.Button(self.frame_control, text='Stop')
        self.button_stop.grid(GRID_CNF, row=0, column=5)

        self.button_close = tk.Button(self.frame_control, text='Close')
        self.button_close.grid(GRID_CNF, row=0, column=8)

        self.frame_chat = tk.LabelFrame(self.frame, PADDING_CNF, text='Chat')
        self.frame_chat.grid(GRID_CNF)
        self.frame_chat.grid_rowconfigure(index=0, weight=1)
        self.frame_chat.grid_columnconfigure(index=0, weight=1)

        self.textbox_chat = tk.Text(self.frame_chat)
        self.textbox_chat.grid(GRID_CNF)
