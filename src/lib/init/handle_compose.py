from hashlib import sha256
from functools import partial
from python_on_whales import DockerClient, DockerException
from yaml import safe_load

CHUNK_SIZE = 4096
SERVERS_COMPOSE_FILE_PATH = "./resources/compose_files/docker-game-compose.yaml"
FRONTEND_COMPOSE_FILE_PATH = "./resources/compose_files/docker-frontend-compose.yaml"

#MASTER_COMPOSE_FILE_PATH = "./compose.yaml"

def hash_compose_file() -> str:
    sha_hash = sha256()
    final_hash = ""

    with open(SERVERS_COMPOSE_FILE_PATH, "rb") as file:
        for chunk in iter(partial(file.read, CHUNK_SIZE), b""):
            sha_hash.update(chunk)
    
    final_hash += sha_hash.hexdigest()

    with open(FRONTEND_COMPOSE_FILE_PATH, "rb") as file:
        for chunk in iter(partial(file.read, CHUNK_SIZE), b""):
            sha_hash.update(chunk)

    final_hash += sha_hash.hexdigest()

    return final_hash

def docker_compose():
    try:
        docker = DockerClient(compose_files=(SERVERS_COMPOSE_FILE_PATH))
        docker.compose.down()
        docker.compose.up(build=True, start=False)

        docker = DockerClient(compose_files=(FRONTEND_COMPOSE_FILE_PATH))
        docker.compose.down()
        docker.compose.up(build=True, start=False)
        docker.wait("frontend_database")
        return True
    
    except DockerException as e:
        print(f'Exited compose with error {e}')
        return False
    
def format_compose_file():
    data = None
    with open(SERVERS_COMPOSE_FILE_PATH, "r") as f:
        data = safe_load(f)
        services = data.get('services', {})

        for service in services:
            if service == "frontend": continue

            services[service]["volumes"] = ["${SERVER_DATA_PATH}/"+f'{service}:/data']
            services[service]["working_dir"] = "/data"

    with open(SERVERS_COMPOSE_FILE_PATH, "w") as f:
        f.write(_convert_obj_to_str(data)[0])

    return True

def _convert_obj_to_str(obj, depth=0):
    if (not (type(obj) is dict)): 
        if (not (type(obj) is list)): return f'{obj}' + "\n", False

        string = "\n"

        for value in obj:
            string += "  "*depth + f'- {value}' + "\n" 
        return string, False

    string = ''

    for values in obj:
        formatted_str, is_dict = _convert_obj_to_str(obj[values], depth+1)

        string += "  "*depth + f'{values}: {"\n" if is_dict else ""}{formatted_str}'

    if depth == 2 or depth == 1:
        string += "\n"

    return string, True