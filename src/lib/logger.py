from sys import stdout
from typing import TextIO, Callable
from collections import deque

LOGGERS = {}

class logger:
    def __init__(self, name:str, log_callback:Callable=None, stdout:TextIO=stdout):
        self.stdout = stdout
        self.log_callback = log_callback

        self.history = deque(maxlen=100)

        LOGGERS[name] = self

    def change_log_cb(self, cb:callable):
        self.log_callback = cb

    def log(self, *msg:str) -> None:
        print(msg, file=self.stdout)

        self.history.append(msg)

        if self.log_callback:
            self.log_callback(msg)

    def get_history(self):
        return self.history

    def print(self, *msg:str) -> None:
        print(*msg, file=self.stdout)

def get_logger(logger_name:str, log_callback:Callable=None, stdout:TextIO=stdout) -> logger:
    if (logger_name in LOGGERS and not log_callback): return LOGGERS[logger_name]
    if (logger_name in LOGGERS): 
        LOGGERS[logger_name].change_log_cb(log_callback)
        return LOGGERS[logger_name]

    return add_logger(logger_name, log_callback, stdout)

def add_logger(logger_name:str, log_callback:Callable=None, stdout:TextIO=stdout) -> None:
    return logger(logger_name, log_callback, stdout)