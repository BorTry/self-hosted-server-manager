from json import load
from os import cpu_count
from python_on_whales import docker, DockerException

CLIENT = docker
SERVER_JSON = None
CORE_COUNT = cpu_count()

with open("./servers.json", "r") as file:
    SERVER_JSON = load(file)

def docker_running():
    try:
        CLIENT.system.info()
        return True
    except DockerException:
        return False
    
def convert_container_name(container_name:str):
    return container_name.replace("_server", "")

def convert_server_name(server_name:str):
    return f'{SERVER_JSON["server_names_to_container"][server_name]}_server'

def get_container(container_name:str, all=False):
    container = CLIENT.ps(filters={"name":container_name}, all=all)
    if (not container):
        print(f"container {container_name} does not exist, or is not running")
        return False

    return container

def get_container_count(all:bool=False):
    return len(CLIENT.ps(all=all))

def get_container_names(all:bool=False):
    fin_arr = []
    containers = CLIENT.ps(all=all)

    # Filter out the names
    for con in containers:
        fin_arr.append(con.name)

    return fin_arr

# ============================ Container stats ============================

def get_resource_use_for_containers():
    fin_arr = []

    all_containers = CLIENT.stats()

    for server in all_containers:
        c_name = convert_container_name(server.container_name)
        if (not (c_name in SERVER_JSON["container_to_server_names"])): continue

        print(server)

        fin_arr.append(
            {
                "name": SERVER_JSON["container_to_server_names"][c_name],
                "ram": server.memory_percentage,
                "cpu": server.cpu_percentage
            }
        )

    return fin_arr

def wait_for_shutdown(container_name):
    container = get_container(container_name)

    if not container:
        return
    
    container.wait()

# ============================ Container manipulation ============================

def stop_frontend(): 
    # check to see if the docker container exists at all
    if (not len(CLIENT.ps(filters={"name": "frontend_server"}))):
        raise Exception("Front end container is not running")
    
    CLIENT.stop("frontend_server")
    CLIENT.wait("frontend_server")

def start_frontend(): 
    # check to see if the docker container exists at all
    if (not len(CLIENT.ps(filters={"name": "frontend_server"}, all=True))):
        raise Exception("Front end container does not exist")
    
    CLIENT.start("frontend_server")

def stop_server(server_name:str):
    container_name = convert_server_name(server_name)
    container = get_container(container_name)

    if (not container): return

    CLIENT.stop(container_name)

def start_server(server_name:str):
    container_name = convert_server_name(server_name)
    container = get_container(container_name, True)

    if (not container): return

    CLIENT.start(container_name)

def restart_server(server_name:str):
    container_name = convert_server_name(server_name)
    container = get_container(container_name)

    if (not container): return

    CLIENT.restart(container_name)