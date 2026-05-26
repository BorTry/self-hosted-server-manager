from src.lib import thread_socket_wrapper
from src.lib import Server_codes

GOT_ALL_SERVERS = False

def socket_func(thread:thread_socket_wrapper):
    global GOT_ALL_SERVERS

    if (not GOT_ALL_SERVERS):
        socket_init(thread)
        return

    data = thread.send_recv(Server_codes.RUNNING_SERVERS, "")

    if (not data): 
        thread.return_val = None
    else:
        thread.return_val = data["data"]

def socket_init(thread:thread_socket_wrapper):
    global GOT_ALL_SERVERS

    data = thread.send_recv(Server_codes.ALL_SERVERS, "")

    if (not data): return

    GOT_ALL_SERVERS = True
    thread.return_val = data["data"]