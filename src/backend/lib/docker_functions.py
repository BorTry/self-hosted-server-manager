from json import load
from os import cpu_count
from python_on_whales import docker, DockerException

SERVER_JSON = None
CORE_COUNT = cpu_count()

with open("./servers.json", "r") as file:
    SERVER_JSON = load(file)

def docker_running():
    try:
        docker.system.info()
        return True
    except DockerException:
        return False
    
def convert_container_name(container_name:str):
    return container_name.replace("_server", "")

def convert_server_name(server_name:str):
    return f'{SERVER_JSON["server_names_to_container"][server_name]}_server'

def get_container(container_name:str, all=False):
    container = docker.ps(filters={"name":container_name}, all=all)
    if (not container):
        print(f"container {container_name} does not exist, or is not running")
        return False

    return container

def get_container_count(all:bool=False):
    return len(docker.ps(all=all))

def get_container_names(all:bool=False):
    fin_arr = []
    containers = docker.ps(all=all)

    # Filter out the names
    for con in containers:
        fin_arr.append(con.name)

    return fin_arr

# ============================ Container stats ============================

def get_resource_use_for_containers():
    fin_arr = []

    all_containers = docker.ps()
    all_stats = docker.stats()

    memory_usage = {}
    cpu_usage = {}

    # map the memory usage to each container name
    for server in all_stats:
        c_name = convert_container_name(server.container_name)
        if (not (c_name in SERVER_JSON["container_to_server_names"])): continue

        memory_usage[c_name] = server.memory_percentage
        cpu_usage[c_name] = server.cpu_percentage

    for server in all_containers:
        c_name = convert_container_name(server.name)
        if (not (c_name in SERVER_JSON["container_to_server_names"]) or not (c_name in memory_usage)): continue

        fin_arr.append(
            {
                "name": SERVER_JSON["container_to_server_names"][c_name],
                "ram": memory_usage[c_name],
                "cpu": cpu_usage[c_name] / get_cpu(server)
            }
        )

    return fin_arr

def get_cpu(container) -> float | None:
    if container.host_config.nano_cpus:
        return container.host_config.nano_cpus / 1_000_000_000

    if container.host_config.cpu_quota and container.host_config.cpu_period:
        return container.host_config.cpu_quota / container.host_config.cpu_period

    if container.host_config.cpuset_cpus:
        return len(container.host_config.cpuset_cpus.split(","))

    return None

def wait_for_shutdown(container_name):
    container = get_container(container_name)

    if not container:
        return
    
    container.wait()

# ============================ Container manipulation ============================

def stop_frontend(): 
    # check to see if the docker container exists at all
    if (not len(docker.ps(filters={"name": "frontend_server"}))):
        raise Exception("Front end container is not running")
    
    docker.stop("frontend_server")
    docker.wait("frontend_server")
    docker.stop("frontend_database")

def start_frontend(): 
    # check to see if the docker container exists at all
    if (not len(docker.ps(filters={"name": "frontend_server"}, all=True))):
        raise Exception("Front end container does not exist")
    
    docker.start("frontend_database")
    docker.start("frontend_server")

def stop_server(server_name:str):
    container_name = convert_server_name(server_name)
    container = get_container(container_name)

    if (not container): return

    docker.stop(container_name)

def start_server(server_name:str):
    container_name = convert_server_name(server_name)
    container = get_container(container_name, True)

    if (not container): return

    docker.start(container_name)

def restart_server(server_name:str):
    container_name = convert_server_name(server_name)
    container = get_container(container_name)

    if (not container): return

    docker.restart(container_name)