"""
Run function for the docker thread
"""
from src.lib.ez_thread import ez_thread
from src.lib.server_codes import Server_codes
from src.backend.lib.docker_functions import *

CONTAINERS = [None] * 10

def docker_func(thread:ez_thread):
    # get all running servers
    all_containers = filter_container_names(get_container_names())
    resources_used = get_resource_use_for_containers(all_containers)

    CONTAINERS[Server_codes.RUNNING_SERVERS] = resources_used

    thread.send(CONTAINERS)
    
    data_packet = thread.recv()

    if (not data_packet): return
    # use the data to try to start or stop a server
    match (data_packet["code"]):
        case Server_codes.START_SERVER:
            start_server(data_packet["data"]["name"])
        case Server_codes.STOP_SERVER:
            stop_server(data_packet["data"]["name"])

# send over data to the com thread
def docker_init(thread:ez_thread):
    CONTAINERS[Server_codes.ALL_SERVERS] = {
        "servers": SERVER_JSON["server_names"],
        "launch_options": SERVER_JSON["launch_alternatives"]
    }