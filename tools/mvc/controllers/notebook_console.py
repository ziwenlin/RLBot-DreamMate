from mvc.models.application_window import ApplicationModel
from mvc.views.application_window import ApplicationView
from networking.threads import SimpleThread


class NotebookConsoleController:
    def __init__(self, view: ApplicationView, model: ApplicationModel, name: str, thread: SimpleThread):
        self.view = view
        self.model = model
        self.name = name
        self.thread = thread

        self.console = self.view.spawn_console(name)
        self._bind()

    def _bind(self):
        self.console.button_close.config(command=lambda: self.close_notebook())
        self.console.button_start.config(command=lambda: self.start_thread())
        self.console.button_stop.config(command=lambda: self.stop_thread())
        self.console.button_send.config(command=lambda: self.send_message())

        self.console.entry_message.bind('<Return>', lambda e: self.send_message())
        self.console.frame.after(1000, self.receive_message)

    def receive_message(self):
        message = self.thread.queues.get()
        while message is not None:
            self.log_message_incoming(message)
            message = self.thread.queues.get()
        self.console.frame.after(1000, self.receive_message)

    def send_message(self):
        message = self.console.read_message_entry()
        if message == '':
            self.log_info('Message is empty')
            return
        self.thread.queues.put(message)
        self.log_message_outgoing(message)
        # self.console.clear_message()

    def log_message_incoming(self, text: str):
        self.console.write_console(f'[Chat] <<< {text}\n')

    def log_message_outgoing(self, text: str):
        self.console.write_console(f'[Chat] >>> {text}\n')

    def log_info(self, text: str):
        self.console.write_console(f'[Info] {text}\n')

    def open_notebook(self):
        if self.name in self.view.consoles:
            return
        self.view.append_console(self.name, self.console)

    def close_notebook(self):
        if self.thread.is_alive():
            self.log_info('Thread is still running.')
            return
        self.view.remove_console(self.name)

    def start_thread(self):
        if self.thread.is_alive():
            self.log_info('Thread already running')
            return
        self.thread = self.thread.__class__()
        self.thread.start()
        self.log_info('Thread has started')

    def stop_thread(self):
        if self.thread.is_alive() is False:
            self.log_info('Thread is not running')
            return
        self.thread.stop()
        self.log_info('Thread has been stopped')
