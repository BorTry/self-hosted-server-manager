from json import load
from python_on_whales import docker, DockerException
from time import sleep

SERVER_JSON = None

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

def get_all_containers():
    fin_arr = []

    all_containers = docker.ps(all=True)
    all_stats = docker.stats()

    resource_usage = {}

    # map the memory usage to each container name
    for server in all_stats:
        c_name = convert_container_name(server.container_name)
        if (not (c_name in SERVER_JSON["container_to_server_names"])): continue

        resource_usage[c_name] = {
            "ram": server.memory_percentage,
            "cpu": server.cpu_percentage,
            "upload": server.net_upload,
            "download": server.net_download
        }

    for server in all_containers:
        c_name = convert_container_name(server.name)
        if (not (c_name in SERVER_JSON["container_to_server_names"]) or not (c_name in resource_usage)): continue

        fin_arr.append(
            {
                "name": SERVER_JSON["container_to_server_names"][c_name],
                "ram": resource_usage[c_name]["ram"],
                "cpu": resource_usage[c_name]["cpu"] / get_cpu(server),
                "upload": resource_usage[c_name]["upload"],
                "download": resource_usage[c_name]["download"]
            }
        )

    return fin_arr

def get_resource_limit_containers():
    all_containers = docker.ps(all=True)

    resource_usage = {}
    for server in all_containers:
        c_name = convert_container_name(server.name)
        if (not (c_name in SERVER_JSON["container_to_server_names"])): continue

        resource_usage[SERVER_JSON["container_to_server_names"][c_name]] = {
            "ram_limit": server.host_config.memory / 1_000_000_000,
            "cpu_limit": get_cpu(server)
        }
        
        ports = server.host_config.port_bindings
        resource_usage[SERVER_JSON["container_to_server_names"][c_name]]["ports"] = []

        for port_binding in ports:
            container_port, container_port_type = port_binding.split("/")
            host_port = ports[port_binding][0].host_port

            resource_usage[SERVER_JSON["container_to_server_names"][c_name]]["ports"].append({
                "container_port": container_port,
                "port_type": container_port_type,
                "host_port": host_port
            })

    return resource_usage

def get_cpu(container) -> float:
    if container.host_config.nano_cpus:
        return container.host_config.nano_cpus / 1_000_000_000

    if container.host_config.cpu_quota and container.host_config.cpu_period:
        return container.host_config.cpu_quota / container.host_config.cpu_period

    if container.host_config.cpuset_cpus:
        return len(container.host_config.cpuset_cpus.split(","))

    return 1.0

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

def start_frontend(): 
    # check to see if the docker container exists at all
    if (not len(docker.ps(filters={"name": "frontend_server"}, all=True))):
        raise Exception("Front end container does not exist")
    
    docker.start("frontend_database")
    docker.start("frontend_server")
    database = docker.ps(all=True, filters={"name": "frontend_database"})[0]

    print("Waiting for database to start...")
    for _ in range(30):
        database.reload()

        health = database.state.health.status if database.state.health else None

        if health == "healthy":
            print("Database is ready.")
            return

        sleep(1)
    raise TimeoutError("Database did not start correctly")

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