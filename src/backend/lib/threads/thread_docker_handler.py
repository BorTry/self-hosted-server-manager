from ..docker import *
from src.lib import thread_wrapper, Server_codes, compose_file

from src.db.mappings import launch_opts_view
from src.db.db import SessionLocal

from sqlalchemy import select
from python_on_whales import DockerClient

COMPOSE_FILE = "./resources/compose_files/docker-game-compose.yaml"
DOCKER_CLIENT = DockerClient(compose_files=(COMPOSE_FILE))

def docker_handler_func(thread:thread_wrapper):
    requests = thread.data_handler.get_copy("requests")
    responses = thread.data_handler.get_copy("responses")

    with thread.data_handler as data:
        data["requests"] = []

    if (not len(requests)): return
    
    for data_packet in requests:
        match (data_packet.code):
            case Server_codes.START_SERVER:
                thread.print("data_packet:", data_packet.data)
                if (len(data_packet.data["opt"])):
                    thread["compose_file"].update()
                    launch_vars = _get_launch_opts(thread, data_packet.data)
                    thread.print("launch vars: ", launch_vars)
                    _prepare_server(thread, data_packet.data["name"], launch_vars)

                start_server(data_packet.data["name"])

            case Server_codes.STOP_SERVER:
                stop_server(data_packet.data["name"])

            case Server_codes.RESTART_SERVER:
                restart_server(data_packet.data["name"])

    with thread.data_handler as data:
        data["responses"] = responses

def docker_handler_init(thread:thread_wrapper):
    thread["compose_file"] = compose_file(COMPOSE_FILE)

def _get_launch_opts(thread:thread_wrapper, container:str):
    # retrieve the launch options from the database
    # check if there are any launch options

    launch_opts = {}

    with SessionLocal() as session:
        rows = session.scalars(select(launch_opts_view).where(launch_opts_view.s_name == container["name"])).all()

    for row in rows:
        if not (row.lom_name in launch_opts):
            launch_opts[row.lom_name] = {
                "source": row.source,
                "handling": row.handling,
                "change_var": row.change_var,
                "file_path": row.file_path,
                "var_flag": row.var_flag,
            }

            match (row.source):
                case 0:
                    launch_opts[row.lom_name]["mapping"] = {}
                case 1:
                    launch_opts[row.lom_name]["mapping"] = []
                case _:
                    thread.print(f"Source {row.source} does not exist in 'launch_option_mapping'")

        match (row.source):
            case 0:
                launch_opts[row.lom_name]["mapping"][row.lo_name] = {"value": row.value}
            case 1:
                launch_opts[row.lom_name]["mapping"].append(row.path)
            case _:
                thread.print(f"Source {row.source} does not exist in 'launch_option_mapping'")

    for opt in container["opt"]:
        thread.print("opt", opt)
        if not (opt["lom_name"] in launch_opts):
            thread.print(f"There are no launch entry for lom_name {opt["lom_name"]}")
            continue

        entry = launch_opts[opt["lom_name"]]
        source = entry["source"]

        match (source):
            case 0: # injection variable
                launch_opts[opt["lom_name"]]["mapping"] = entry["mapping"][opt["lo_name"]]
            case 1: # file variable
                thread.print(entry["mapping"])
                # got to get the file extension
                launch_opts[opt["lom_name"]]["mapping"] = {"value": f".{entry["mapping"][0]}/{opt["lo_name"]}"}
            case _:
                pass

    return launch_opts

def _prepare_server(thread:thread_wrapper, container_name:str, launch_variables:dict):
    container_name_compose_file = convert_container_name(convert_db_name_docker(container_name))
    container_env = thread["compose_file"].services[container_name_compose_file]["environment"]
    INJECTED_VALUES = False

    if (container_env is None): return
    
    # wipe the original environment launch variables
    var_mapping = {"SEED_SCRIPT": container_env["SEED_SCRIPT"]}
    it = 0

    for key, value in launch_variables.items():
        print(value, flush=True)
        if (value["handling"] != 0): continue

        print("var_flag", value["var_flag"] is not None, not (value["var_flag"] == ""))

        var_mapping[f"LAUNCH_ARG_{it * 2}"] = f"--{value["var_flag"]}" if value["var_flag"] is not None and not (value["var_flag"] == "") else " "
        var_mapping[f"LAUNCH_ARG_{(it * 2) + 1}"] = value["mapping"]["value"] if value["mapping"]["value"] is not None else ""

        it += 1
        INJECTED_VALUES = True

    thread["compose_file"].services[container_name_compose_file]["environment"] = var_mapping

    if (INJECTED_VALUES): thread["compose_file"].write_to_file()

    DOCKER_CLIENT.compose.up(services=container_name_compose_file, recreate=True, build=True, start=False, detach=True)
    thread.print(thread["compose_file"].services[container_name_compose_file], "\n", container_name_compose_file, "\n", launch_variables)