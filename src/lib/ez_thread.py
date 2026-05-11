from threading import Thread, Event
from sys import stdout
from time import sleep

# Typing for very nice :)  
from typing import Callable, Any
from multiprocessing.connection import Connection

class ez_thread:
    __slots__ = ("name", "target", "stdout", "sleep_time", "thread", "terminate_signal", "return_val", "pipe", "init")

    def __init__(self, target:Callable=None, init:Callable=None, terminate_signal:Event=None, name="thread", pipe:Connection=None, sleep_time:float=0.1):
        self.name = name
        self.stdout = stdout
        self.sleep_time = sleep_time

        if not target:
            raise Exception("target function must be defined")

        self.target = target
        self.thread = Thread(target=thread_wrapper(self, target), name=name)
        self.terminate_signal = terminate_signal or Event()
        self.return_val = None

        self.pipe = pipe

        self.init = init

    def print(self, *msg:tuple[str]):
        print(self.name, "->", *msg, file=stdout)

    def recv(self, timeout:bool=True):
        if (self.is_pipe_closed() or (timeout and not self.data_in_pipe())): return

        val = self.pipe.recv()

        return val
    
    def is_pipe_closed(self):
        return self.pipe.closed

    def send(self, val:Any):
        if (self.pipe.closed): return

        self.pipe.send(val)

    def data_in_pipe(self):
        return self.pipe.poll(timeout=0.5)

    def terminate(self):
        # Check if the pipe is still open
        if (self.pipe and not self.pipe.closed):
            self.pipe.close()

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

    def get_new_instance(self, pipe:Connection=None):
        return ez_thread(self.target, self.init, self.terminate_signal, self.name, pipe, self.sleep_time)

def thread_wrapper(self:ez_thread, target:Callable):
    def wrap():
        while not self.terminate_signal.is_set():
            target(self)

            sleep(self.sleep_time)

    return wrap