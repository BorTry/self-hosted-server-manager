from src.lib import thread_wrapper, Server_codes, CONSTANTS
from src.backend.lib.docker_functions import *

from src.db.mappings import metric_timestamp, traffic_metric, performance_metric, container
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
    now = datetime.now()

    if (not last_save or (now - last_save).seconds > save_interval.seconds) and len(resources_used):
        add_resources_to_db(resources_used)
        last_save = now

    with thread.data_handler as data:
        data["data"] = CONTAINERS
        requests = data["requests"]

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
    global save_interval
    
    save_interval = timedelta(seconds=CONSTANTS.METRICS_INTERVAL)

    CONTAINERS[Server_codes.ALL_SERVERS] = {
        "servers": SERVER_JSON["server_names"],
        "launch_options": SERVER_JSON["launch_alternatives"]
    }

    add_containers_to_db(CONTAINERS[Server_codes.ALL_SERVERS]["servers"])

    with thread.data_handler as data:
        data["data"] = CONTAINERS

def add_containers_to_db(containers):
    with SessionLocal() as session:
        for container_entry in containers:
            query = select(container).where(container.name == container_entry)
            entry = session.scalars(query).first()

            if (entry): continue

            session.add(container(name=container_entry))
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