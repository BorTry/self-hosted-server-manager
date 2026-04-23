from json import load
from docker import from_env, errors
from os import cpu_count

CLIENT = from_env()
SERVER_JSON = None
CORE_COUNT = cpu_count()

with open("./servers.json", "r") as file:
    SERVER_JSON = load(file)

def docker_running():
    try:
        CLIENT.ping()
        return True
    except errors.DockerException:
        return False
    
def convert_container_name(container_name:str):
    return container_name.replace("docker_server-", "").split("-")[0]

def convert_server_name(server_name:str):
    return f'docker_server-{SERVER_JSON["server_names_to_container"][server_name]}-1'

def get_container(container_name:str, all=False):
    if (not CLIENT.containers.list(filters={"name":container_name}, all=all)):
        print(f"container {container_name} does not exist")
        return False

    return CLIENT.containers.get(container_name)

def get_container_count(all:bool=False):
    return len(CLIENT.containers.list(all=all))

def get_container_names(all:bool=False):
    fin_arr = []
    containers = CLIENT.containers.list(all=all)

    # Filter out the names
    for con in containers:
        fin_arr.append(con.name)

    return fin_arr

def filter_container_names(container_names:str):
    fin_arr = []
    # Filters out the actual name of the containers, for predefined names / prettier names :)
    for con_name in container_names:
        cut_down_name = convert_container_name(con_name)

        if not (cut_down_name in SERVER_JSON["container_to_server_names"]):
            continue

        fin_arr.append(SERVER_JSON["container_to_server_names"][cut_down_name])
    return fin_arr

# ============================ Container stats ============================

def get_resource_use_for_containers(server_names:tuple[str]):
    fin_arr = []

    for server_name in server_names:
        container = get_container(convert_server_name(server_name))

        if (not container): continue

        stats = get_container_stats(container)
        
        if (not stats): continue
        
        fin_arr.append(
            {
                "name": server_name,
                "ram": get_container_ramusage(stats),
                "cpu": get_cpu_percentage(stats)
            }
        )

    return fin_arr

def get_container_stats(container):
    if (not container): return False

    stats = container.stats(stream=False)

    if (not ("memory_stats" in stats) or not ("cpu_stats" in stats)): return False

    return stats

def get_cpu_percentage(stats):
    try:
        # Calculate deltas between current and previous stats 
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]

        if system_delta > 0.0 and cpu_delta > 0.0:
            print(round((cpu_delta / system_delta) * 100.0))
            return round((cpu_delta / system_delta) * 100.0)
        return 0.0
    except:
        return 0

def get_container_ramusage(stats):
    try:
        mem_usage = stats["memory_stats"]["usage"]
        # Subtract cache to get precise active memory (varies by cgroup version)
        cache = stats["memory_stats"]["stats"].get("inactive_file", 0) 
        used_memory = mem_usage - cache
        limit = stats["memory_stats"]["limit"]

        return round((used_memory / limit) * 100) # out of 100
    except:
        return 0

# ============================ Container manipulation ============================

def stop_frontend(): 
    # check to see if the docker container exists at all
    if (not len(CLIENT.containers.list(filters={"name": "docker_server-frontend-1"}))):
        raise Exception("Front end container is not running")
    
    frontend = CLIENT.containers.get("docker_server-frontend-1")
    frontend.stop()

def start_frontend(): 
    # check to see if the docker container exists at all
    if (not len(CLIENT.containers.list(filters={"name": "docker_server-frontend-1"}, all=True))):
        raise Exception("Front end container does not exist")
    
    frontend = CLIENT.containers.get("docker_server-frontend-1")
    frontend.start()

def stop_server(server_name:str):
    container_name = convert_server_name(server_name)
    container = get_container(container_name)

    if (not container): return

    container = CLIENT.containers.get(container_name)
    container.stop()

def start_server(server_name:str):
    container_name = convert_server_name(server_name)
    container = get_container(container_name, True)

    if (not container): return

    container = CLIENT.containers.get(container_name)
    container.start()