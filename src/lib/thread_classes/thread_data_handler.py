from multiprocessing import Lock
from typing import Any
from copy import deepcopy

class thread_data_handler:
    """
    simple data handler. ensures locking and unlocking of a resource so it can be used by several threads

    Args:
        data (Any): What data structure the data should be put into.
    """
    __slots__ = ("_lock", "_data")
    
    def __init__(self, data:Any):
        self._lock = Lock()
        self._data = data

    def __enter__(self):
        self._lock.acquire()
        return self._data

    def __exit__(self, exc_type, exc, tb):
        self._lock.release()
        return False

    def get_copy(self, index:int|str=None):
        with self._lock:
            if index != None:
                return deepcopy(self._data[index])
            return deepcopy(self._data)