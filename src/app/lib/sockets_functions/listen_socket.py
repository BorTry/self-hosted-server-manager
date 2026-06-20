from src.lib import thread_socket_wrapper
from src.lib import Server_codes
from src.lib import response

def listen_socket_func(thread:thread_socket_wrapper):
    response, _ = thread.recv()

    if response is None: return

    thread.print(f"Recieved: {response}")

    with thread.data_handler as data:
        subscribers = data["subscribers"]

        subscribers[response.id].put(response.data)

def listen_socket_init(thread:thread_socket_wrapper):
    pass