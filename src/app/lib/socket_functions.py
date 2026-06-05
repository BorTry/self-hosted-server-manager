from src.lib import thread_socket_wrapper
from src.lib import Server_codes
from src.lib import request

from multiprocessing import Queue

def socket_func(thread:thread_socket_wrapper):
    if (len(thread["all_servers"]) == 0):
        socket_init(thread)
        return

    packet = thread.send_recv(request(None, "", Server_codes.RUNNING_SERVERS))

    if packet != None:
        with thread.data_handler as thread_data:
            thread_data["running_servers"] = packet.data

    pending_requests = thread.data_handler.get_copy("pending_requests")
    for pending_request in pending_requests:
        thread["responses"].append(thread.send_recv(pending_request))

    with thread.data_handler as thread_data:
        thread_data["pending_requests"] = []

        subscribers = thread_data["subscribers"]

        for response in thread["responses"]:
            if response.code >= Server_codes.ADD_CONTAINER:
                subscribers[response.id].put(response.data)

    thread["responses"] = []

def socket_init(thread:thread_socket_wrapper):
    thread["all_servers"] = []
    thread["launch_options"] = []

    thread["id_sub_mapping"] = {}
    thread["responses"] = []

    data = thread.send_recv(request(None, "", Server_codes.ALL_SERVERS))

    if (not data): return

    thread["all_servers"] = data.data["servers"]
    thread["launch_options"] = data.data["launch_options"]

def get_next_id(thread:thread_socket_wrapper):
    with thread.data_handler as data:
        id = data["current_id"]
        data["current_id"] += 1

        return id

def add_subscriber(thread:thread_socket_wrapper, session_id):
    with thread.data_handler as data:
        data["subscribers"][session_id] = Queue(maxsize=10)

        return data["subscribers"][session_id]