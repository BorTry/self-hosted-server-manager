"""
Run function for the docker thread
"""
from src.lib import thread_wrapper, Server_codes
from src.backend.lib.docker_functions import *

CONTAINERS = [None] * 10

def docker_func(thread:thread_wrapper):
    # get all running servers
    all_containers = filter_container_names(get_container_names())
    resources_used = get_resource_use_for_containers(all_containers)

    CONTAINERS[Server_codes.RUNNING_SERVERS] = resources_used
    requests = []

    with thread.data_handler as data:
        data["data"] = CONTAINERS
        requests = data["requests"]

    #thread.print(requests)

    if (not len(requests)): return
    # use the data to try to start or stop a server
    for data_packet in requests:
        match (data_packet["code"]):
            case Server_codes.START_SERVER:
                start_server(data_packet["data"]["name"])
            case Server_codes.STOP_SERVER:
                stop_server(data_packet["data"]["name"])
            case Server_codes.RESTART_SERVER:
                restart_server(data_packet["data"]["name"])

    with thread.data_handler as data:
        data["requests"] = []

# send over data to the com thread
def docker_init(thread:thread_wrapper):
    CONTAINERS[Server_codes.ALL_SERVERS] = {
        "servers": SERVER_JSON["server_names"],
        "launch_options": SERVER_JSON["launch_alternatives"]
    }

    with thread.data_handler as data:
        data["data"] = CONTAINERS