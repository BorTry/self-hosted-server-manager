from src.lib.sock_thread import sock_thread
from src.lib.server_codes import Server_codes

def socket_func(thread:sock_thread):
    data = thread.send_recv(Server_codes.RUNNING_SERVERS, "")

    if (not data): 
        thread.return_val = None
    else:
        thread.return_val = data["data"]

def socket_init(thread:sock_thread):
    data = thread.send_recv(Server_codes.ALL_SERVERS, "")

    if (not data): return

    thread.return_val = data["data"]