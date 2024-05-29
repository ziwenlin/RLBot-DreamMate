from mvc.models.application_window import ApplicationModel
from mvc.views.application_window import ApplicationView


class ApplicationController:
    def __init__(self, view: ApplicationView, model: ApplicationModel):
        self.view = view
        self.model = model

        self._bind()

    def _bind(self):
        self.view.server_console.button_spawn_client.config(command=self.create_client)
        self.view.server_console.button_disconnect_all.config(command=self.remove_all_clients)

    def _bind_client(self, name: str):
        client = self.view.clients[name]
        client.button_disconnect.config(command=lambda: self.view.remove_client(name))

    def run(self):
        self.view.root.mainloop()

    def create_client(self):
        clients = self.view.clients
        name = 'test'
        for index in range(10):
            name_indexed = name + str(index)
            if name_indexed in clients:
                continue
            name = name_indexed
            break
        self.view.create_client(name)
        self._bind_client(name)

    def remove_all_clients(self):
        for name in list(self.view.clients.keys()):
            self.view.remove_client(name)
