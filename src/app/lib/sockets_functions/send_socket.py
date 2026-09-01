from src.lib import thread_socket_wrapper, Server_codes, request

from time import sleep

def send_socket_func(thread:thread_socket_wrapper):
    """if (len(thread["files"]) == 0):
        sleep(1)
        thread.print("Trying to get defined servers again")
        send_socket_init(thread)
        return"""

    # regular updates
    packet = thread.send_recv(request(None, "", Server_codes.RUNNING_SERVERS))

    if packet != None:
        if type(packet) == bool or type(packet.data) == bool: return

        with thread.data_handler as thread_data:
            if not packet.data:
                thread_data["running_servers"] = {}
            else:
                for server in packet.data:
                    if (type(server["name"]) is int) :
                        print("This server had an int name:", server["name"], "\nBody:\n", server)
                        continue
                    thread_data["running_servers"][server["name"]] = server

    pending_requests = thread.data_handler.get_copy("pending_requests")
    # send all pending requests and wait for them to return
    if len(pending_requests) > 0:
        for pending_request in pending_requests:
            thread.send(pending_request)

    with thread.data_handler as thread_data:
        thread_data["pending_requests"] = []

def send_socket_init(thread:thread_socket_wrapper):
    thread["files"] = []

    server_response = thread.send_recv(request(None, "", Server_codes.SERVER_FILES))

    if (server_response is None or server_response.data is None): return

    try:
        with thread.data_handler as data:
            data["files"] = server_response.data
    except Exception as e:
        thread.print(e)