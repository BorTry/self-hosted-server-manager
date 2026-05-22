from multiprocessing import Lock
from typing import Any

class thread_data_handler:
    """
    simple data handler. ensures locking and unlocking of a resource so it can be used by several threads

    Args:
        data (Any): What data structure the data should be put into.
    """
    def __init__(self, data:Any):
        self.lock = Lock()
        self.data = data

    def __enter__(self):
        self.lock.acquire()
        return self.data

    def __exit__(self, exc_type, exc, tb):
        self.lock.release()