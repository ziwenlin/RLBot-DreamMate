from mvc.models.application_window import ApplicationModel
from mvc.views.application_window import ApplicationView


class ApplicationController:
    def __init__(self, view: ApplicationView, model: ApplicationModel):
        self.view = view
        self.model = model

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
        consoles = self.view.consoles
        name = 'Server'
        for index in range(10):
            name_indexed = f'{name} {index + 1}'
            if name_indexed in consoles:
                continue
            name = name_indexed
            break
        self.view.spawn_console(name)
        self._bind_console(name)

    def create_client(self):
        consoles = self.view.consoles
        name = 'Client'
        for index in range(10):
            name_indexed = f'{name} {index + 1}'
            if name_indexed in consoles:
                continue
            name = name_indexed
            break
        self.view.spawn_console(name)
        self._bind_console(name)
