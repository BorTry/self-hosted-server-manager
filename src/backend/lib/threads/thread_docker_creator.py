from ..docker import *
from src.lib import thread_wrapper, Server_codes, response

from json import dumps

def docker_creator_func(thread:thread_wrapper):
    requests = thread.data_handler.get_copy("requests")
    responses = thread.data_handler.get_copy("responses")

    if (not len(requests)): return

    for data_packet in requests:
        match (data_packet.code):
            case Server_codes.ADD_CONTAINER:
                response_data = try_to_add_container(thread, data_packet)
                response_data["data"]['name'] = data_packet.data["server_name"]
                response_data["data"]['server_id'] = data_packet.data["server_id"]

                response_data["data"] = dumps(response_data["data"])

                responses.append(response(data_packet.id, **response_data))

            case Server_codes.CHANGE_CONTAINER:
                pass

    with thread.data_handler as data:
        data["requests"] = []
        data["responses"] = responses

# send over data to the com thread
def docker_creator_init(thread:thread_wrapper):
    pass