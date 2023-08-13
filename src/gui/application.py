import random
import threading
import time
import tkinter as tk
import multiprocessing

from gui.graph import Graph


def has_game_focus():
    '''Checks whether Rocket League has window focus.'''
    import platform
    if platform.system() not in 'Windows':
        return True
    try:
        import pygetwindow
    except ModuleNotFoundError as e:
        print('Error (can be ignored):', e)
        return True
    # When the game title is empty
    # the game might be in full screen
    # so return true in that case.
    window = pygetwindow.getActiveWindow()
    return window.title in '' or 'Rocket League' in window.title


def has_tkinter_focus():
    '''Checks whether tkinter has window focus.'''
    import platform
    if platform.system() not in 'Windows':
        return True
    try:
        import pygetwindow
    except ModuleNotFoundError as e:
        print('Error (can be ignored):', e)
        return True
    # Tkinter has window focus
    # Choosing cmd here because it is easier to select
    window = pygetwindow.getActiveWindow()
    return 'cmd.exe' in window.title  # or 'DreamMate' in window.title


class AppRunnable:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_event = multiprocessing.Event()
        self.queue_in = multiprocessing.Queue()

    def send(self, message):
        self.queue_in.put(message)

    def run(self) -> None:
        for thread in threading.enumerate():
            if thread.name == 'Tkinter' and thread is not self:
                thread.join()
        app = Application(self.stop_event, self.queue_in)
        if has_game_focus() is True:
            app.wm_iconify()
        elif has_tkinter_focus() is True:
            app.wm_iconify()
            app.after(1000, app.wm_deiconify)
        app.mainloop()
        app.quit()

    def stop(self):
        self.stop_event.set()


class AppThread(AppRunnable, threading.Thread):
    def __init__(self):
        super().__init__(name='Tkinter')


class AppProcess(AppRunnable, multiprocessing.Process):
    def __init__(self):
        super().__init__(name='Tkinter')


class Application(tk.Tk):
    def __init__(self, event: threading.Event, queue_in: multiprocessing.Queue):
        super().__init__()
        self.event = event
        self.queue_in = queue_in

        self.frame = tk.Frame(self)
        self.frame.pack(fill='both', expand=True)

        self.graph = Graph(self.frame)
        self.graph.pack(expand=True, fill='both')

        self.graph.plot.set_xlim(-1, 10)
        self.graph.plot.set_ylim(-1, 10)

        self.after(100, lambda: self.poll_data())
        self.after(100, lambda: self.poll_running())

    def poll_running(self):
        if self.event.is_set():
            self.quit()
            return
        self.after(100, lambda: self.poll_running())

    def poll_data(self):
        self.after(100, lambda: self.poll_data())
        if self.queue_in.empty():
            return
        for _ in range(1000):
            if self.queue_in.empty():
                break
            message = self.queue_in.get()
            data = self.process_message(message)
            self.process_graph(data)
        key = next(iter(self.graph.lines.keys()))
        self.graph.size_line(key, 5000)
        self.graph.view_line(key)
        self.graph.draw()

    def process_message(self, message):
        point = None
        key = 'line'
        if type(message) is str:
            message: str
            data = message.split(':')
            key = data.pop(0)
            value = float(data.pop(0))
            if len(data) > 0:
                point = float(data.pop(0))
        else:
            value = float(message)
        return key, value, point

    def process_graph(self, data):
        key, value, point = data
        if key not in self.graph.lines:
            if point is None:
                point = 0
            self.graph.create_line(key, value=value, point=point - 1)
        self.graph.extend_line(key, value, point)


def main():
    process = AppProcess()
    process.start()

    import timeit
    for _ in range(10):
        time.sleep(0.1)
        print(timeit.timeit(lambda: process.send(random.random() * 10 - 1), number=10000))

    time.sleep(10)
    process.stop()

    time.sleep(1)
    process.join()


if __name__ == '__main__':
    main()
