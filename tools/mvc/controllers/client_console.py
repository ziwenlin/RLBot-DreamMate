from mvc.controllers.notebook_console import NotebookConsoleController
from mvc.models.application_window import ApplicationModel
from mvc.views.application_window import ApplicationView
from networking.clients import ClientThread


class ClientConsoleController(NotebookConsoleController):
    def __init__(self, view: ApplicationView, model: ApplicationModel, name: str):
        super().__init__(view, model, name, ClientThread())
