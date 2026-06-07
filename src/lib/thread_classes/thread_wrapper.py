from threading import Thread, Event

from typing import Callable

from .thread_data_handler import thread_data_handler
from ..logger import get_logger

class thread_wrapper:
    __slots__ = ("name", "logger", "target", "stdout", "sleep_time", "thread", "terminate_signal", "return_val", "data_handler", "init", "_data")

    def __init__(self, target:Callable=None, init:Callable=None, terminate_signal:Event=None, name="thread", data_handler:thread_data_handler=None, sleep_time:float=0.1):
        self.name = name
        self.sleep_time = sleep_time

        if not target:
            raise Exception("target function must be defined")

        self.target = target
        self.thread = Thread(target=thread_function_wrapper(self, target), name=name)
        self.terminate_signal = terminate_signal or Event()
        self.return_val = None

        self.data_handler = data_handler
        self.logger = get_logger(name)

        self.init = init

        self._data = {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, key):
        return key in self._data

    def print(self, *msg:tuple[str]):
        self.logger.print(*msg)

    def log(self, *msg:tuple[str]):
        self.logger.print(*msg)

    def terminate(self):
        self.print("Stopping")

        # Close the thread and wait for it to finish
        if (not self.terminate_signal.is_set()):
            self.terminate_signal.set() # Multiple threads can use the same event signal

        if self.thread and self.thread.is_alive():
            print(f"Waiting for {self.thread.name} to terminate")
            self.thread.join()

    def run(self):
        self.print(f"Starting {self.name}")
        if (self.init):
            self.init(self)
        self.print(f"{self.name} has been initialized")

        self.thread.start()

    def get_new_instance(self):
        return thread_wrapper(self.target, self.init, self.terminate_signal, self.name, self.data_handler, self.sleep_time)

def thread_function_wrapper(self:thread_wrapper, target:Callable):
    def wrap():
        while not self.terminate_signal.is_set():
            target(self)

            self.terminate_signal.wait(self.sleep_time)

    return wrap