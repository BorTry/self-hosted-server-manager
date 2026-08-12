from multiprocessing import Lock as L
from multiprocessing.synchronize import Lock

from typing import Any
from copy import deepcopy

class thread_data_handler:
    """
    Initialize a thread-safe data handler.

    Args:
        data (Any): Data managed by handler
        lock (Lock | None): Optional existing lock to share with another
            handler. If omitted, a new lock is created automatically.
    
    Returns:
        thread_data_handler: A handler referencing the selected subsection.
    """

    __slots__ = ("_lock", "_data")

    def __init__(self, data:Any, lock:Lock=None):
        self._lock = lock if lock is not None else L()
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

    def get_subsection(self, index:int|str=None):
        """
        Create a data handler for a subsection of the managed data.

        The returned handler references the original data at ``index`` rather
        than creating a copy. It shares the same lock as the parent handler.

        Args:
            index (int | str): Index or key of the subsection.

        Returns:
            thread_data_handler: A handler referencing the selected subsection.
        """
        return thread_data_handler(self._data[index], self._lock)