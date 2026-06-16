from hashlib import sha256
from functools import partial
from python_on_whales import DockerClient, DockerException
from yaml import safe_load

from .. import compose_file

CHUNK_SIZE = 4096

SERVERS_COMPOSE_FILE_PATH = "./resources/compose_files/docker-game-compose.yaml"
FRONTEND_COMPOSE_FILE_PATH = "./resources/compose_files/docker-frontend-compose.yaml"
IMAGE_COMPOSE_FILE_PATH = "./resources/compose_files/docker-base-compose.yaml"

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

def docker_compose() -> bool:
    try:
        print("Setting up user servers...")
        docker = DockerClient(compose_files=(IMAGE_COMPOSE_FILE_PATH))
        docker.compose.build()
        docker.compose.down()

        print("Setting up user servers...")
        docker = DockerClient(compose_files=(SERVERS_COMPOSE_FILE_PATH))
        docker.compose.down()
        docker.compose.up(build=True, start=False)

        print("Setting up frontend servers...")
        docker = DockerClient(compose_files=(FRONTEND_COMPOSE_FILE_PATH))
        docker.compose.down()
        docker.compose.up(build=True, start=False)
        docker.wait("frontend_database")
        
        return True
    
    except DockerException as e:
        print(f'Exited compose with error {e}')
        return False
    
def format_compose_file() -> bool:
    compose_structure = compose_file(SERVERS_COMPOSE_FILE_PATH)
    
    services = compose_structure.services

    for service_name in services:
        service = services[service_name]

        if (service["volumes"] is None):
            service["volumes"] = ["${SERVER_DATA_PATH}/"+f'{service_name}:/data']
        elif not (f"${{SERVER_DATA_PATH}}/{service_name}:/data" in service["volumes"]):
            service["volumes"].append(f"${{SERVER_DATA_PATH}}/{service_name}:/data")

        service["working_dir"] = "/data"

        print(service)
    
    compose_structure.write_to_file()

    return True