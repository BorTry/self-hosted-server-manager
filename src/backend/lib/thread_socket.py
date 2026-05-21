from src.lib import thread_socket_wrapper, Server_codes

def socket_func(thread:thread_socket_wrapper):
    data_packet, from_address = thread.recv()

    if (not data_packet): return

    with thread.data_handler as data:
        server_data = data["data"].copy()

    return_data = None
    incoming_data = None

    match(data_packet["code"]):
        case Server_codes.SERVER_COUNT:
            return_data = len(server_data[Server_codes.RUNNING_SERVERS]) # Send how many server are currently running
        case Server_codes.RUNNING_SERVERS:
            return_data = server_data[Server_codes.RUNNING_SERVERS] # Send a list of all running servers
        case Server_codes.ALL_SERVERS:
            return_data = server_data[Server_codes.ALL_SERVERS] # Send a list of all available server

        case Server_codes.START_SERVER|Server_codes.STOP_SERVER:
            incoming_data = data_packet
        case _:
            thread.print(f"There are no functions for code {data_packet['code']}")

    if (return_data):
        thread.send(return_data, target=from_address)

    elif (incoming_data):
        thread.print("appending request ->", f'{incoming_data}')
        
        with thread.data_handler as data:
            data["requests"].append(incoming_data)