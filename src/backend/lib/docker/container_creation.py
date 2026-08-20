from src.lib import thread_wrapper, compose_file, service, Server_codes, response
from .detect_steady_state import check_run_command

from src.db.mappings import metric_timestamp, traffic_metric, performance_metric, container, port_type, ports, ports_mapping, launch_opts_mapping, launch_opts
from src.db.db import SessionLocal

from sqlalchemy import select

from python_on_whales import DockerClient, DockerException, docker as base_docker
from re import sub, DOTALL
from pathlib import Path

from json import dumps, loads

TEMP_COMPOSE_PATH = "./resources/compose_files/docker-temp-compose.yaml"
MAIN_COMPOSE_PATH = "./resources/compose_files/docker-game-compose.yaml"

TEMP_COMPOSE_FILE = compose_file(TEMP_COMPOSE_PATH)
MAIN_COMPOSE_FILE = compose_file(MAIN_COMPOSE_PATH)

DOCKER_AI_MSG_REG = r"\n?\x1b\[[0-9;]*mWhat's next:.*"

SERVER_DATA_FILE_PATH = Path(Path(__file__).resolve().parents[5], "server_data")

if (not SERVER_DATA_FILE_PATH.is_dir()):
    SERVER_DATA_FILE_PATH.mkdir()

def try_to_add_container(thread:thread_wrapper, server_packet) -> bool:
    compose_args = server_packet.data

    thread.print(compose_args)
    server_name = compose_args["server_name"]

    new_container = service(
        name=server_name,
        container_name=server_name+"_server",
        cpus=str(compose_args["cpu_limit"])+".0",
        mem_limit=compose_args["ram_limit"]+"GB",
        command=compose_args["launch_opt"],
        image="base_image",
        working_dir="/data",
    )

    # add dicts and arrays
    new_container["ports"] = compose_args["port_mapping"]
    new_container["volumes"] = [f"${{SERVER_DATA_PATH}}/{server_name}:/data"]
    new_container["entrypoint"] = ["/entrypoint.sh"]
    new_container["environment"] = {"SEED_SCRIPT": compose_args["install_opt"]}

    _add_container_to_server(compose_args)
    TEMP_COMPOSE_FILE.add_service(new_container)
    TEMP_COMPOSE_FILE.write_to_file()

    return_message = _test_new_container(thread, new_container,server_packet)

    TEMP_COMPOSE_FILE.remove_service(new_container.name)
    TEMP_COMPOSE_FILE.write_to_file()

    return return_message

def _test_new_container(thread:thread_wrapper, new_container:service, server_packet):
    docker = DockerClient(compose_files=(TEMP_COMPOSE_PATH))

    # check to see if the container builds
    with thread.data_handler as data:
        data["responses"].append(response(server_packet.id, **_generate_current_status_msg("Building...", server_packet)))

    try:
        docker.compose.build(services=(new_container.name), quiet=True)
    except DockerException as e:
        return _generate_return_msg(True, sub(DOCKER_AI_MSG_REG, '', f"Container failed to build -> Check your settings\nError was: {e}", flags=DOTALL))

    # check the install/seed script
    if (not _has_been_initialized(new_container.name)):
        with thread.data_handler as data:
            data["responses"].append(response(server_packet.id, **_generate_current_status_msg("Installing...", server_packet)))

        try:
            docker.compose.up(services=(new_container.name), quiet=True, detach=False)
        except DockerException as e:
            return _generate_return_msg(True, sub(DOCKER_AI_MSG_REG, '', f"Container failed to run -> Check your launch command\nError was: {e}", flags=DOTALL))

        container = docker.container.inspect(new_container.name+"_server")
        exit_code = container.state.exit_code

        if exit_code != 0 or not _has_been_initialized(new_container.name):
            return _generate_return_msg(True, f"Install script failed -> Check your install command\nLast 10 log lines were:\n{docker.logs(new_container.name+"_server", tail=10)}")

    else:
        thread.print(f"Skipping initialization step for server '{new_container.name}'")

    # check to see if the actual launch function runs'
    with thread.data_handler as data:
        data["responses"].append(response(server_packet.id, **_generate_current_status_msg("Running...", server_packet)))

    docker.compose.up(services=(new_container.name), quiet=True, detach=True)

    run_command_worked = check_run_command(thread, new_container.name)

    docker.stop(new_container.name+"_server")

    if not run_command_worked:
        return _generate_return_msg(True, f"Container failed to run -> Check your launch command\nLast 10 log lines were:\n{docker.logs(new_container.name+"_server", tail=10)}")

    docker.compose.down(services=(new_container.name), quiet=True)

    #MAIN_COMPOSE_FILE.add_service(new_container)
    #MAIN_COMPOSE_FILE.write_to_file()

    return _generate_return_msg(False)

def _generate_current_status_msg(status:str, server_packet):
    return {
        "code": Server_codes.CONTAINER_WORKING,
        "data": dumps({"status":status, "name":server_packet.data["server_name"], "server_id":server_packet.data["server_id"]})
    } 


def _generate_return_msg(failure:bool, message:str=None):
    return {
        "code": Server_codes.CONTAINER_FAILED if failure else Server_codes.CONTAINER_SUCCESS,
        "data": {'msg': message, 'success': not failure}
    }

def _has_been_initialized(server_name):
    return Path(SERVER_DATA_FILE_PATH, server_name).is_dir() and Path(SERVER_DATA_FILE_PATH, server_name, ".initialized").is_file()


def _add_container_to_server(server_args):
    with SessionLocal() as session:
        container_name_exists = session.scalar(select(container).where(container.name == server_args["server_name"]))

        if (container_name_exists is not None):
            return

        port_types_rows = session.execute(select(port_type)).mappings().all()
        port_type_mapping = {}

        for port in port_types_rows:
            port_type_mapping[port["port_type"].type] = port["port_type"].id

        entry = container(
            name = server_args["server_name"],
            ram_limit = server_args["cpu_limit"],
            cpu_limit = server_args["ram_limit"], 
        )

        session.add(entry)
        session.flush()

        if (len(server_args["port_mapping"])):

            mapping_db_entry = ports_mapping(server_id=entry.id)

            session.add(mapping_db_entry)
            session.flush()

            for port_str in server_args["port_mapping"]:
                current_port = _get_ports_from_str(port_str)
                
                if (server_args["strict_ports"]):
                    return

                session.add(ports(
                    mapping_id=mapping_db_entry.id,
                    container_port=current_port["server"],
                    host_port=current_port["host"], 
                    type_id=port_type_mapping[current_port["type"]]
                ))

        if (len(server_args["variable_mapping"])):
            loaded_var_map = loads(server_args["variable_mapping"])

            for key, value in loaded_var_map.items():
                mapping_has_path = len(value["file_path"].values()) > 0

                launch_mapping = launch_opts_mapping(
                    name = key,
                    path = value["file_path"]["path"] if mapping_has_path else "",
                    change_var = value["file_path"]["change_var"] if mapping_has_path else "",
                    container_id = entry.id,
                    handling = 0 if value["value_state"] == "false" else 1,
                    source = 0 if value["source_state"] == "false" else 1
                )

                session.add(launch_mapping)
                session.flush()

                for variable_mapping in value["mapping"]:
                    session.add(launch_opts(
                        mapping_id = launch_mapping.id,
                        name = variable_mapping["name"],
                        value = variable_mapping["value"],
                        path = variable_mapping["path"]
                    ))

        #session.commit()

def _get_ports_from_str(port_str):
    split_ports = port_str.split(":")
    port_type = split_ports[1].split("/")

    return {"host":split_ports[0], "server":port_type[0], "type":port_type[1].lower()}