from src.lib import thread_socket_wrapper, Server_codes, CONSTANTS

def socket_func(thread:thread_socket_wrapper):
    data_packet, from_address = thread.recv()

    if (not data_packet): return

    with thread.data_handler as data:
        server_data = data["data"].copy()

    return_data = None
    incoming_data = None
    code = Server_codes.OK

    data = data_packet["data"]

    match(data_packet["code"]):
        case Server_codes.SERVER_COUNT:
            return_data = len(server_data[Server_codes.RUNNING_SERVERS]) # Send how many server are currently running
        case Server_codes.RUNNING_SERVERS:
            return_data = server_data[Server_codes.RUNNING_SERVERS] # Send a list of all running servers
        case Server_codes.ALL_SERVERS:
            return_data = server_data[Server_codes.ALL_SERVERS] # Send a list of all available server

        case Server_codes.START_SERVER|Server_codes.STOP_SERVER:
            incoming_data = data_packet

        case Server_codes.CHECK_CREDENTIALS:
            return_data = True
            code = Server_codes.BAD
            if data["username"] == CONSTANTS.CREDENTIALS["username"] and data["password"] == CONSTANTS.CREDENTIALS["password"]:
                code = Server_codes.CREDENTIALS_OK
            thread.print(f'User "{data["username"]}" with password "{data["password"]}" is trying to log in.')

        case _:
            thread.print(f"There are no functions for code {data_packet['code']}")

    if (return_data):
        thread.send(return_data, code, target=from_address)

    elif (incoming_data):
        thread.print("appending request ->", f'{incoming_data}')
        
        with thread.data_handler as data:
            data["requests"].append(incoming_data)