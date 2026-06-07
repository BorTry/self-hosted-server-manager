from multiprocessing import Queue
from datetime import datetime, timezone

class logger:
    LOGGERS = Queue(maxsize=100)

    @staticmethod
    def print_all(self):
        while True:
            if logger.LOGGERS.empty(): break
            print(*logger.LOGGERS.get())

    @staticmethod
    def logger(logger_name:str=""):
        class custom_logger:
            def __init__(self, log_name):
                self.mother_queue = logger.LOGGERS
                self.name = log_name

            def print(self, *msg):
                self.mother_queue.put([datetime.now(timezone.utc).strftime("[%H:%M:%S]"), self.name, "->", *msg])

            def log(self, *msg):
                self.mother_queue.put([datetime.now(timezone.utc).strftime("[%H:%M:%S]"), self.name, "->", *msg])

        return custom_logger(logger_name)

get_logger = logger.logger