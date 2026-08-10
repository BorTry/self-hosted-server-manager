from src.lib import thread_socket_wrapper

from math import ceil

MAX_MESSAGE_SIZE = 4096

def listen_socket_func(thread:thread_socket_wrapper):
    response, _ = thread.recv()

    if response is None or response.id is None: return

    data_size = len(f"{response.data!r}".encode("utf-8"))

    with thread.data_handler as data:
        subscribers = data["subscribers"]

        if data_size > MAX_MESSAGE_SIZE:
            split_messages = ceil(data_size / MAX_MESSAGE_SIZE)

            for i in range(split_messages):
                start = MAX_MESSAGE_SIZE * i
                end = MAX_MESSAGE_SIZE * (i + 1)

                subscribers[response.id].put({"type":"batch", "data":f"{response.data[start:end]!r}"})
            subscribers[response.id].put({"type":"end", "data":""})
        else:
            subscribers[response.id].put({"type":"update", "data":response.data})

def listen_socket_init(thread:thread_socket_wrapper):
    pass