from typing import Dict

from mvc.models.application_window import ApplicationModel
from mvc.views.application_window import ApplicationView


class ApplicationController:
    def __init__(self, view: ApplicationView, model: ApplicationModel):
        self.view = view
        self.model = model

        self.view.entry_server_address.insert(0, self.model.server_address)
        self.view.entry_server_port.insert(0, self.model.server_port)

        self._bind()

    def _bind(self):
        self.view.button_spawn_client.config(command=self.create_client)
        self.view.button_spawn_server.config(command=self.create_server)

    def _bind_console(self, name: str):
        console = self.view.consoles[name]
        console.button_close.config(command=lambda: self.view.remove_console(name))

    def run(self):
        self.view.root.mainloop()

    def create_server(self):
        name = self._create_unique_console_name('Server')
        self.view.spawn_console(name)
        self._bind_console(name)

    def create_client(self):
        name = self._create_unique_console_name('Client')
        self.view.spawn_console(name)
        self._bind_console(name)

    def _create_unique_console_name(self, name: str):
        consoles = self.view.consoles
        if name not in consoles:
            return name
        for index in range(10):
            name_indexed = f'{name} {index + 1}'
            if name_indexed in consoles:
                continue
            return name_indexed
        return name

    def _get_address_and_port(self):
        address = self.view.entry_server_address.get()
        port = self.view.entry_server_port.get()
        return address, port

    def _is_address_and_port_valid(self):
        address, port = self._get_address_and_port()
        if address == '' and port == '':
            return False
        return True
