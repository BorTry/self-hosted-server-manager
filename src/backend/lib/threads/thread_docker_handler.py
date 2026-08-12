from ..docker import *
from src.lib import thread_wrapper, Server_codes

def docker_handler_func(thread:thread_wrapper):
    requests = thread.data_handler.get_copy("requests")
    responses = thread.data_handler.get_copy("responses")

    with thread.data_handler as data:
        data["requests"] = []

    if (not len(requests)): return
    
    for data_packet in requests:
        match (data_packet.code):
            case Server_codes.START_SERVER:
                start_server(data_packet.data["name"])

            case Server_codes.STOP_SERVER:
                stop_server(data_packet.data["name"])

            case Server_codes.RESTART_SERVER:
                restart_server(data_packet.data["name"])

    with thread.data_handler as data:
        data["responses"] = responses

def docker_handler_init(thread:thread_wrapper):
    pass