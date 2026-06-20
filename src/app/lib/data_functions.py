from .sockets import DATA_HANDLER
from src.lib import request

import queue

def get_next_id():
    with DATA_HANDLER as data:
        id = data["current_id"]
        data["current_id"] += 1

        return id

def add_subscriber(session_id:int):
    with DATA_HANDLER as data:
        data["subscribers"][session_id] = queue.Queue(maxsize=10)

        return data["subscribers"][session_id] # return the queue
    
def add_request(request_obj:request):
    with DATA_HANDLER as data:
        data["pending_requests"].append(request_obj)