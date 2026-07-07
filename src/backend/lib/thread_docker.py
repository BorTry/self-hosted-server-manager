from .docker import *
from .thread_container_logger import logger_generator, add_session_id, remove_session_id

from src.lib import thread_wrapper, Server_codes, CONSTANTS, response
from src.db.mappings import metric_timestamp, traffic_metric, performance_metric, container, port_type, ports, ports_mapping
from src.db.db import SessionLocal
from sqlalchemy import select

from datetime import timedelta, datetime

CONTAINERS = [None] * 10

def docker_func(thread:thread_wrapper):
    # get all running servers
    running_containers = get_all_containers()

    CONTAINERS[Server_codes.RUNNING_SERVERS] = running_containers
    requests = []
    responses = []
    now = datetime.now()

    if len(running_containers) and (not thread["last_save"] or (now - thread["last_save"]).seconds > thread["save_interval"].seconds):
        add_resources_to_db(running_containers)
        thread["last_save"] = now

    with thread.data_handler as data:
        data["data"] = CONTAINERS
        requests = data["requests"]
        responses = data["responses"]

    if (not len(requests)): return
    # use the data to try to start or stop a server
    thread.print(*requests)

    for data_packet in requests:
        match (data_packet.code):
            case Server_codes.START_SERVER:
                start_server(data_packet.data["name"])
            case Server_codes.STOP_SERVER:
                stop_server(data_packet.data["name"])
            case Server_codes.RESTART_SERVER:
                restart_server(data_packet.data["name"])
            case Server_codes.ADD_CONTAINER:
                response_data = try_to_add_container(thread, data_packet.data)
                
                responses.append(response(data_packet.id, **response_data))
            case Server_codes.LOG_CONTAINER:
                server_name = data_packet.data["server_name"]
                container_name = convert_server_name(server_name)

                if not (container_name in thread["logger_threads"]):
                    generate_new_log_thread(thread, container_name, data_packet.id)

                add_session_id(thread["logger_threads"][container_name], data_packet.id)

            case Server_codes.CHANGE_CONTAINER:
                pass

    with thread.data_handler as data:
        data["requests"] = []
        data["responses"] = responses

# send over data to the com thread
def docker_init(thread:thread_wrapper):
    CONTAINERS[Server_codes.ALL_SERVERS] = {
        "servers": SERVER_JSON["server_names"],
        "launch_options": SERVER_JSON["launch_alternatives"]
    }

    thread["logger_threads"] = {}
    thread["save_interval"] = timedelta(seconds=CONSTANTS.METRICS_INTERVAL)
    thread["last_save"] = datetime.now()

    add_containers_to_db(thread, CONTAINERS[Server_codes.ALL_SERVERS]["servers"], get_resource_limit_containers())

    with thread.data_handler as data:
        data["data"] = CONTAINERS

def docker_on_close(thread:thread_wrapper):
    if (len(thread["logger_threads"]) > 0):
        for logger_name in thread["logger_threads"]:
            thread["logger_threads"][logger_name].terminate()

def add_containers_to_db(thread:thread_wrapper, containers, limits):  
    with SessionLocal() as session:
        port_types_rows = session.execute(select(port_type)).mappings().all()
        port_type_mapping = {}

        for port in port_types_rows:
            port_type_mapping[port["port_type"].type] = port["port_type"].id

        for container_el in containers:
            query = select(container).where(container.name == container_el)
            entry = session.scalars(query).first()

            if (not entry): 
                entry = container(
                    name = container_el,
                    ram_limit = limits[container_el]["ram_limit"],
                    cpu_limit = limits[container_el]["cpu_limit"], 
                )
                session.add(entry)
                session.flush()


            if len(limits[container_el]["ports"]):
                existing_ports_query = select(ports.host_port) \
                    .join(ports_mapping, ports_mapping.id == ports.mapping_id) \
                    .where(ports_mapping.server_id == entry.id)
                
                rows = session.execute(existing_ports_query).mappings().all()
                existing_ports = [row["host_port"] for row in rows]

                for port in limits[container_el]["ports"]:
                    if int(port["host_port"]) in existing_ports: 
                        thread.print(f"post {port['host_port']} already exists for container {entry.name}. Skipping")
                        continue

                    mapping_db_entry = ports_mapping(server_id=entry.id)
                    session.add(mapping_db_entry)
                    session.flush()

                    session.add(ports(
                        mapping_id=mapping_db_entry.id,
                        container_port=port["container_port"],
                        host_port=port["host_port"], 
                        type_id=port_type_mapping[port["port_type"]]
                    ))

        session.commit()

def add_resources_to_db(resources):
    with SessionLocal() as session:
        stamp = metric_timestamp()

        session.add(stamp)
        session.commit()

        for container_entry in resources:
            query = select(container).where(container.name == container_entry["name"])
            entry = session.scalars(query).first()

            session.add(performance_metric(container_id=entry.id, time_id=stamp.id, cpu=container_entry["cpu"], ram=container_entry["ram"]))
            session.add(traffic_metric(container_id=entry.id, time_id=stamp.id, upload=container_entry["upload"], download=container_entry["download"]))

        session.commit()

def generate_new_log_thread(thread:thread_wrapper, server_name:str, session_id:int):
    thread.print(f'Generating new thread for server: {server_name}')

    try:
        log_thread = logger_generator(server_name, thread.terminate_signal)
    except Exception as e:
        thread.print(f'got an error while setting up new log thread for server: {server_name}\n{e!r}')
        return

    thread["logger_threads"][server_name] = log_thread