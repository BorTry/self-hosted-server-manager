from hashlib import sha256
from functools import partial
from python_on_whales import DockerClient, DockerException, docker as base_docker

from .. import compose_file

from shutil import copy

CHUNK_SIZE = 4096

MAPPING = {
    "base": "./resources/compose_files/docker-base-compose.yaml",
    "server": "./resources/compose_files/docker-game-compose.yaml",
    "frontend": "./resources/compose_files/docker-frontend-compose.yaml"
}

COMPOSE_MSG = {
    "base": "Setting up base image...",
    "server": "Setting up user servers...",
    "frontend": "Setting up frontend servers..."
}

def check_compose_files(json_hash_obj):   
    _format_servers_compose_file()

    for key in MAPPING:
        new_hash = _hash_compose_file(key)

        if json_hash_obj[f"{key}_hash"] == new_hash: continue

        if (not _docker_compose_file(key)):
            raise RuntimeError(f"Something went wrong while composing {key}")

        json_hash_obj[f"{key}_hash"] = new_hash

def _hash_compose_file(mapping_name:str) -> str:
    if not (mapping_name in MAPPING):
        raise ValueError(f"{mapping_name} is not a supported mapping")
    
    sha_hash = sha256()
    final_hash = ""

    with open(MAPPING[mapping_name], "rb") as file:
        for chunk in iter(partial(file.read, CHUNK_SIZE), b""):
            sha_hash.update(chunk)

    final_hash = sha_hash.hexdigest()

    return final_hash

def _docker_compose_file(mapping_name:str) -> bool:
    if not (mapping_name in MAPPING):
        raise ValueError(f"{mapping_name} is not a supported mapping")

    try:
        print(COMPOSE_MSG[mapping_name])

        if (mapping_name == "frontend"):
            print("copying over .env variables")
            copy("./.env", "./resources/compose_files/.env")


        docker = DockerClient(compose_files=(MAPPING[mapping_name]))
        docker.compose.up(build=True, detach=True)

        if (mapping_name != "base"): return True
        containers = docker.compose.ps()

        for container in containers:
            docker.wait(container)

        docker.compose.down()
        
        return True
    
    except DockerException as e:
        print(f'Exited compose with error {e}')
        return False
    
def _format_servers_compose_file():
    compose_structure = compose_file(MAPPING["server"])
    
    services = compose_structure.services

    for service_name in services:
        service = services[service_name]

        if (service["volumes"] is None):
            service["volumes"] = ["${SERVER_DATA_PATH}/"+f'{service_name}:/data']
        elif not (f"${{SERVER_DATA_PATH}}/{service_name}:/data" in service["volumes"]):
            service["volumes"].append(f"${{SERVER_DATA_PATH}}/{service_name}:/data")

        service["working_dir"] = "/data"
    
    compose_structure.write_to_file()