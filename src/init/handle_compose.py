from os import path
from hashlib import sha256
from functools import partial
from python_on_whales import DockerClient, DockerException


CHUNK_SIZE = 4096
COMPOSE_FILE_PATH = "./compose.yaml"

def hash_compose_file() -> str:
    sha_hash = sha256()

    with open(COMPOSE_FILE_PATH, "rb") as file:
        for chunk in iter(partial(file.read, CHUNK_SIZE), b""):
            sha_hash.update(chunk)

    return sha_hash.hexdigest()

def docker_compose():
    try:
        docker = DockerClient(compose_files=("./compose.yaml"))

        docker.compose.up(build=True, start=False)
        return True
    
    except DockerException as e:
        print(f'Exited compose with error {e}')
        return False