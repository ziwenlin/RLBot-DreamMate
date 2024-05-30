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

    def _bind_client(self, name: str):
        client = self.view.clients[name]
        client.button_close_client.config(command=lambda: self.view.remove_client(name))

    def _bind_server(self, name: str):
        server = self.view.servers[name]
        server.button_close_server.config(command=lambda: self.view.remove_server(name))

    def run(self):
        self.view.root.mainloop()

    def create_server(self):
        servers = self.view.servers
        name = 'Server'
        for index in range(10):
            name_indexed = f'{name} {index + 1}'
            if name_indexed in servers:
                continue
            name = name_indexed
            break
        self.view.spawn_server(name)
        self._bind_server(name)

    def create_client(self):
        clients = self.view.clients
        name = 'Client'
        for index in range(10):
            name_indexed = f'{name} {index + 1}'
            if name_indexed in clients:
                continue
            name = name_indexed
            break
        self.view.spawn_client(name)
        self._bind_client(name)
