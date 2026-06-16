from src.lib import thread_wrapper, Server_codes, CONSTANTS
from .docker import *

from src.db.mappings import metric_timestamp, traffic_metric, performance_metric, container, port_type, ports, ports_mapping
from src.db.db import SessionLocal
from sqlalchemy import select

from datetime import timedelta, datetime

CONTAINERS = [None] * 10

save_interval = 0
last_save = None

def docker_func(thread:thread_wrapper):
    global save_interval, last_save
    # get all running servers
    resources_used = get_resource_use_for_containers()

    CONTAINERS[Server_codes.RUNNING_SERVERS] = resources_used
    requests = []
    responses = []
    now = datetime.now()

    if (not last_save or (now - last_save).seconds > save_interval.seconds) and len(resources_used):
        add_resources_to_db(resources_used)
        last_save = now

    with thread.data_handler as data:
        data["data"] = CONTAINERS
        requests = data["requests"]
        responses = data["responses"]

    if (not len(requests)): return
    # use the data to try to start or stop a server
    for data_packet in requests:
        match (data_packet.code):
            case Server_codes.START_SERVER:
                start_server(data_packet.data["name"])
            case Server_codes.STOP_SERVER:
                stop_server(data_packet.data["name"])
            case Server_codes.RESTART_SERVER:
                restart_server(data_packet.data["name"])
            case Server_codes.ADD_CONTAINER:
                try_to_add_container(thread, data_packet.data)
            case Server_codes.CHANGE_CONTAINER:
                pass

    with thread.data_handler as data:
        data["requests"] = []
        data["responses"] = responses

# send over data to the com thread
def docker_init(thread:thread_wrapper):
    global save_interval
    
    save_interval = timedelta(seconds=CONSTANTS.METRICS_INTERVAL)

    CONTAINERS[Server_codes.ALL_SERVERS] = {
        "servers": SERVER_JSON["server_names"],
        "launch_options": SERVER_JSON["launch_alternatives"]
    }

    add_containers_to_db(CONTAINERS[Server_codes.ALL_SERVERS]["servers"], get_resource_limit_containers())

    with thread.data_handler as data:
        data["data"] = CONTAINERS

def add_containers_to_db(containers, limits):  
    with SessionLocal() as session:
        port_types_rows = session.execute(select(port_type)).mappings().all()
        port_type_mapping = {}

        for port in port_types_rows:
            port_type_mapping[port["port_type"].type] = port["port_type"].id

        for container_el in containers:
            query = select(container).where(container.name == container_el)
            entry = session.scalars(query).first()

            if (entry): continue
            
            container_db_entry = container(
                name = container_el,
                ram_limit = limits[container_el]["ram_limit"],
                cpu_limit = limits[container_el]["cpu_limit"], 
            )
            session.add(container_db_entry)
            session.flush()

            if len(limits[container_el]["ports"]):
                mapping_db_entry = ports_mapping(server_id=container_db_entry.id)
                session.add(mapping_db_entry)
                session.flush()

                for port in limits[container_el]["ports"]:
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
            session.add(traffic_metric(container_id=entry.id, time_id=stamp.id, up=container_entry["upload"], down=container_entry["download"]))

        session.commit()