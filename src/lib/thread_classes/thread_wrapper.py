from threading import Thread, Event

from typing import Callable

from .thread_data_handler import thread_data_handler
from ..logger import get_logger

from datetime import datetime, timezone

class thread_wrapper:
    __slots__ = ("name", "logger", "on_close", "target", "stdout", "sleep_time", "thread", "terminate_signal", "data_handler", "init", "_data")

    def __init__(self, target:Callable=None, init:Callable=None, on_close:Callable=None, terminate_signal:Event=None, name="thread", data_handler:thread_data_handler=None, sleep_time:float=0.1):
        self.name = name
        self.sleep_time = sleep_time

        if not target:
            raise Exception("target function must be defined")

        self.target = target
        self.thread = Thread(target=thread_function_wrapper(self, target), name=name)
        self.terminate_signal = terminate_signal or Event()

        self.data_handler = data_handler
        self.logger = get_logger(name)

        self.init = init
        self.on_close = on_close

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

    def is_alive(self):
        return not self.terminate_signal.is_set() and self.thread.is_alive()

    def terminate(self):
        print(datetime.now(timezone.utc).strftime("[%H:%M:%S]"), self.thread.name, "->", "Stopping", flush=True)

        # Close the thread and wait for it to finish
        if (not self.terminate_signal.is_set()):
            self.terminate_signal.set() # Multiple threads can use the same event signal

        if self.thread and self.thread.is_alive():
            print(datetime.now(timezone.utc).strftime("[%H:%M:%S]"), self.name, "->", f'Waiting for {self.thread.name} to terminate', flush=True)
            self.thread.join()

    def terminate_next_cycle(self):
        # should only be run on threads that dont share terminate signals
        self.terminate_signal.set()
        self.print("Stopping next cycle")

    def run(self):
        self.print(f"Starting {self.name}")
        if (self.init):
            self.init(self)
        self.print(f"{self.name} has been initialized")

        self.thread.start()

    def get_new_instance(self):
        return thread_wrapper(self.target, self.init, self.on_close, None, self.name, self.data_handler, self.sleep_time)

def thread_function_wrapper(self:thread_wrapper, target:Callable):
    def wrap():
        while not self.terminate_signal.is_set():
            target(self)
            
            if not self.sleep_time: continue

            self.terminate_signal.wait(self.sleep_time)

        if self.on_close is not None:
            self.on_close(self)

    return wrap