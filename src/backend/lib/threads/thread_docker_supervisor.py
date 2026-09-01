from ..docker import *
from src.lib import thread_wrapper, Server_codes, CONSTANTS

from .thread_container_logger import logger_generator, add_session_id, remove_session_id
from src.db.mappings import metric_timestamp, traffic_metric, performance_metric, container, port_type, ports, ports_mapping, launch_opts_view
from src.db.db import SessionLocal

from datetime import timedelta, datetime
from sqlalchemy import select
from copy import deepcopy
from pathlib import Path

def docker_supervisor_func(thread:thread_wrapper):    
    thread["containers"]["running_servers"] = get_all_containers(thread["all_servers"])
    now = datetime.now()

    if len(thread["containers"]["running_servers"]) and (not thread["last_save"] or (now - thread["last_save"]).seconds > thread["save_interval"].seconds):
        _add_resources_to_db(thread["containers"]["running_servers"])

        thread["last_save"] = now
        thread["all_servers"] = get_all_servers() # keep the list updated

    if (now - thread["last_file_check"]).seconds > thread["save_interval"].seconds:
        thread["containers"]["files"] = _get_file_names(thread)
        thread["last_file_check"] = now

    with thread.data_handler as data:
        data["data"] = deepcopy(thread["containers"])

    supervisor_data = thread.data_handler.get_copy("supervisor")

    requests = supervisor_data["requests"]
    responses = supervisor_data["responses"]

    if (not len(requests)): return

    for data_packet in requests:
        match (data_packet.code):
            case Server_codes.LOG_CONTAINER:
                server_name = data_packet.data["server_name"]
                container_name = convert_db_name_docker(server_name)

                _generate_new_log_thread(thread, container_name)

                add_session_id(thread["logger_threads"][container_name], data_packet.id)

            case Server_codes.STOP_LOG_CONTAINER:
                thread.print("Removing id from loggers")
                remove_session_id(thread, data_packet.data["id"])

    with thread.data_handler as data:
        data["supervisor"]["requests"] = []
        data["supervisor"]["responses"] = responses

def docker_supervisor_init(thread:thread_wrapper):
    db_servers = get_all_servers()
    current_servers = []

    if not len(db_servers):
        for server_name in SERVER_JSON["server_names"]:
            current_servers.append(convert_db_name_docker(server_name))
    else:
        current_servers = db_servers
    
    thread["containers"] = {
        "running_servers": [],
        "files": _get_file_names(thread)
    }

    thread["all_servers"] = current_servers

    _add_containers_to_db(thread, thread["all_servers"], get_resource_limit_containers(thread["all_servers"]))

    thread["logger_threads"] = {}
    thread["save_interval"] = timedelta(seconds=CONSTANTS.METRICS_INTERVAL)
    thread["last_save"] = datetime.now()
    thread["last_file_check"] = datetime.now()

def docker_supervisor_on_close(thread:thread_wrapper):
    if (len(thread["logger_threads"]) > 0):
        for logger_name in thread["logger_threads"]:
            thread["logger_threads"][logger_name].terminate()

def _generate_new_log_thread(thread:thread_wrapper, container_name:str):
    if not (container_name in thread["logger_threads"]):
        thread.print(f'Generating new thread for server: {container_name}')

        try:
            log_thread = logger_generator(container_name)
        except Exception as e:
            thread.print(f'got an error while setting up new log thread for server: {container_name}\n{e!r}')
            return

        thread["logger_threads"][container_name] = log_thread
    else:
        # container references might exist, but not run currently
        log_thread = thread["logger_threads"][container_name]

        if (log_thread.is_alive()): return

        thread["logger_threads"][container_name] = log_thread.get_new_instance()
        thread["logger_threads"][container_name].run()

def _add_containers_to_db(thread:thread_wrapper, containers, limits):  
    with SessionLocal() as session:
        port_types_rows = session.execute(select(port_type)).mappings().all()
        port_type_mapping = {}

        for port in port_types_rows:
            port_type_mapping[port["port_type"].type] = port["port_type"].id

        for container_docker_name in containers:
            container_db_name = convert_docker_name_db(container_docker_name)

            query = select(container).where(container.name == container_db_name)
            entry = session.scalars(query).first()

            if (not entry): 
                thread.print(f"Creating new entry for server {container_db_name}")
                entry = container(
                    name = container_db_name,
                    ram_limit = limits[container_db_name]["ram_limit"],
                    cpu_limit = limits[container_db_name]["cpu_limit"], 
                )
                session.add(entry)
                session.flush()

            if limits and container_db_name in limits and len(limits[container_db_name]["ports"]):
                existing_ports_query = select(ports.host_port) \
                    .join(ports_mapping, ports_mapping.id == ports.mapping_id) \
                    .where(ports_mapping.server_id == entry.id)
                
                rows = session.execute(existing_ports_query).mappings().all()
                existing_ports = [row["host_port"] for row in rows]

                for port in limits[container_db_name]["ports"]:
                    if int(port["host_port"]) in existing_ports: 
                        thread.print(f"port {port['host_port']} already exists for container {entry.name}. Skipping")
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

def _add_resources_to_db(resources):
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

def _get_file_names(thread:thread_wrapper):
    with SessionLocal() as session:
        query = select(launch_opts_view.s_name, launch_opts_view.path, launch_opts_view.lom_name).where(launch_opts_view.source == 1)
        rows = session.execute(query).mappings().all()

    directories = []

    for row in rows:
        server_dir = Path(f"../server_data/{convert_container_name(convert_db_name_docker(row.s_name))}{row.path}")

        files = []

        for file in server_dir.iterdir():
            file_name = file.name

            if (file.is_dir()):
                files.append(file.name)
                continue

            files.append(file_name.split(".")[0])

        directories.append({"s_name":row.s_name, "lom_name":row.lom_name, "files":files})

    return directories