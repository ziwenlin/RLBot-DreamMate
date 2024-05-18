import logging
import math
import time
import tkinter as tk

from networking.client import ClientHandler
from networking.server import ServerHandler
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
    logger = logging.getLogger(__name__)
    server = ServerHandler()
    server.start()

    client_list = []
    try:
        for _ in range(10):
            client = ClientHandler()
            client.start()
            client_list.append(client)
    except Exception as e:
        logger.warning('[Main] ' + str(e))

    root = tk.Tk()
    view = Graph(root)
    view.pack()
    controller(view)
    root.mainloop()

    server.stop()
    for client in client_list:
        while client.is_alive():
            time.sleep(1)
    while server.is_alive():
        time.sleep(1)


if __name__ == '__main__':
    main()
