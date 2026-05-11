"""
Run function for the comm thread
"""
from src.lib.ez_thread import ez_thread
from src.lib.server_codes import Server_codes
from src.lib.sock_thread import sock_thread

from threading import Lock
# holds anto a dict that gets updated by the docker thread
# when a request from the frontend server comes in send the requested data from that dict over

DATA_LOCK = Lock()
SERVER_DATA = None
INCOMING_DATA = None

def comm_func(thread:ez_thread):
    global SERVER_DATA, DATA_LOCK, INCOMING_DATA

    data = thread.recv() # TODO: change into a better solution, for more flexibility:)

    if (not data): return

    with DATA_LOCK:
        SERVER_DATA = data

    if (INCOMING_DATA):
        thread.send(INCOMING_DATA)
        INCOMING_DATA = None

def comm_init(thread:ez_thread):
    global SERVER_DATA

    SERVER_DATA = thread.recv(False) # Recieve the initial data from the backend

def socket_func(thread:sock_thread):
    global SERVER_DATA, DATA_LOCK, INCOMING_DATA

    data_packet, from_address = thread.recv()

    if (not data_packet): return

    with DATA_LOCK:
        if (not SERVER_DATA): 
            print(SERVER_DATA)
            return
        server_data = SERVER_DATA.copy()

    return_data = None


    match(data_packet["code"]):
        case Server_codes.SERVER_COUNT:
            return_data = len(server_data[Server_codes.RUNNING_SERVERS]) # Send how many server are currently running
        case Server_codes.RUNNING_SERVERS:
            return_data = server_data[Server_codes.RUNNING_SERVERS] # Send a list of all running servers
        case Server_codes.ALL_SERVERS:
            return_data = server_data[Server_codes.ALL_SERVERS] # Send a list of all available server

        case Server_codes.START_SERVER|Server_codes.STOP_SERVER:
            INCOMING_DATA = data_packet
        case _:
            thread.print(f"There are no functions for code {data_packet['code']}")

    if (not return_data): return
    
    thread.send(return_data, target=from_address)