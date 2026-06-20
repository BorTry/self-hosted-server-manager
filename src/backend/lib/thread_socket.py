from src.lib import thread_socket_wrapper, Server_codes, CONSTANTS, response

from src.db.mappings import connections, login_attempts
from src.db.db import SessionLocal

from sqlalchemy import select
from datetime import datetime, timedelta

TARGET_ADDRESS = None
MAX_ATTEMPTS = 3
ATTEMPT_TIME_DELTA = 10 # minutes

def socket_func(thread:thread_socket_wrapper):
    data_packet, from_address = thread.recv()

    if (not data_packet): return

    server_data = thread.data_handler.get_copy("data")

    return_data = None
    incoming_data = None
    code = Server_codes.OK

    data = data_packet.data
    id = data_packet.id

    match(data_packet.code):
        case Server_codes.SERVER_COUNT:
            return_data = len(server_data[Server_codes.RUNNING_SERVERS]) # Send how many server are currently running
        case Server_codes.RUNNING_SERVERS:
            return_data = server_data[Server_codes.RUNNING_SERVERS] # Send a list of all running servers
        case Server_codes.ALL_SERVERS:
            return_data = server_data[Server_codes.ALL_SERVERS] # Send a list of all available server

        case Server_codes.START_SERVER|Server_codes.STOP_SERVER:
            incoming_data = data_packet

        case Server_codes.CHECK_CREDENTIALS|Server_codes.CHECK_REPEATED_CREDENTIALS:
            return_data = True
            code = verify_login(data)

            if data_packet.code == Server_codes.CHECK_CREDENTIALS: thread.print(f'User "{data["username"]}" with password "{data["password"]}" is trying to log in.')

        case Server_codes.ADD_CONTAINER:
            code = Server_codes.OK
            return_data = f"Recieved data for new container {data["server_name"]}"
            incoming_data = data_packet
            from_address = None
            # quickly verify the data, add to db, and pass on to docker thread
            #code = Server_codes.CONTAINER_FAILED

        case Server_codes.CHANGE_CONTAINER:
            pass

        case _:
            thread.print(f"There are no functions for code {data_packet['code']}")

    if (return_data):
        thread.send(response(id, return_data, code), target=from_address)

    if (incoming_data):
        thread.print("appending request ->", f'{incoming_data}')
        
        with thread.data_handler as data:
            data["requests"].append(incoming_data)

    with thread.data_handler as data:
        if len(data["responses"]) > 0:
            for packet in data["responses"]:
                thread.print(f"Sending packet: {packet!r}")
                thread.send(packet)

            data["responses"] = []

def verify_login(data):
    if data["username"] != CONSTANTS.CREDENTIALS["username"] or data["password"] != CONSTANTS.CREDENTIALS["password"]: return Server_codes.BAD

    with SessionLocal() as session:
        connection_entry = get_ip_entry(session, data["ip"])

        if (connection_entry.blacklisted):
            return Server_codes.BAD

        attempts = get_login_attemps(connection_entry, session)

        if (len(attempts) >= MAX_ATTEMPTS):
            connection_entry.blacklisted = True
            session.commit()

            print(f'Blacklisting ip: {data["ip"]}')
            return Server_codes.BAD

        new_login_entry = login_attempts(connection_id=connection_entry.id)
        session.add(new_login_entry)
        session.commit()
        
        new_login_entry.failed_login = False
        session.commit()

        return Server_codes.CREDENTIALS_OK

def get_ip_entry(session, ip):
    ip_query = select(connections).where(connections.ip == ip)

    connection_entry = session.scalars(ip_query).first()

    if not connection_entry:
        connection_entry = connections(ip=ip)
        print("Creating new database entry")
        session.add(connection_entry)
        session.commit()

    return connection_entry

def get_login_attemps(entry, session):
    cutoff = datetime.now() - timedelta(minutes=ATTEMPT_TIME_DELTA)

    # check the amount of recent login attempts that failed
    login_attempts_query = select(login_attempts).where(
        login_attempts.connection_id == entry.id, 
        login_attempts.failed_login == True,
        login_attempts.time >= cutoff
    )
    return session.scalars(login_attempts_query).all()