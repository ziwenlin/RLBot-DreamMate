import math
import tkinter as tk

from mvc.controllers.application_window import ApplicationController
from mvc.models.application_window import ApplicationModel
from mvc.views.application_window import ApplicationView
from networking.clients import ClientThread
from networking.servers import ServerThread
from rendering.graph import Graph


def controller(view: Graph):
    class Model:
        x = 0
        y = 0

        def update(self):
            self.x += 0.1
            self.y = math.sin(self.x)

    model = Model()

    line_name = 'Hello World!'
    view.create_line(line_name)

    def program():
        model.update()
        view.extend_line(line_name, model.y, model.x)
        view.after(10, program)

    def render():
        view.view_line(line_name)
        view.draw()
        view.after(800, render)

    view.after(1000, render)
    view.after(1000, program)


def main():
    server = ServerThread()
    server.start()

    client_list = []
    for _ in range(3):
        client = ClientThread()
        client.start()
        client_list.append(client)

    root = tk.Tk()
    view = Graph(root)
    view.pack()
    controller(view)
    root.mainloop()

    for client in client_list:
        client.stop()
        client.join()
    server.stop()
    server.join(1)


def main_tk():
    main_view = ApplicationView()
    main_model = ApplicationModel()
    main_controller = ApplicationController(main_view, main_model)
    main_controller.run()


if __name__ == '__main__':
    main_tk()
