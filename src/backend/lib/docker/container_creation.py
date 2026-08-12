from src.lib import thread_wrapper, compose_file, service, Server_codes

from python_on_whales import DockerClient, DockerException, docker as base_docker
from re import sub, DOTALL
from time import sleep
from pathlib import Path

TEMP_COMPOSE_PATH = "./resources/compose_files/docker-temp-compose.yaml"
MAIN_COMPOSE_PATH = "./resources/compose_files/docker-game-compose.yaml"

TEMP_COMPOSE_FILE = compose_file(TEMP_COMPOSE_PATH)
MAIN_COMPOSE_FILE = compose_file(MAIN_COMPOSE_PATH)

DOCKER_AI_MSG_REG = r"\n?\x1b\[[0-9;]*mWhat's next:.*"

SERVER_DATA_FILE_PATH = Path(Path(__file__).resolve().parents[5], "server_data")

if (not SERVER_DATA_FILE_PATH.is_dir()):
    SERVER_DATA_FILE_PATH.mkdir()

def try_to_add_container(thread:thread_wrapper, compose_args) -> bool:
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

    if (False):
        # create a docker buildfile if the image needs any extra dependencies
        new_container["build"] = {"context": "../buildfiles", "dockerfile": f"Dockerfile.{server_name}"}

    TEMP_COMPOSE_FILE.add_service(new_container)
    TEMP_COMPOSE_FILE.write_to_file()

    return_message = _test_new_container(thread, new_container)

    TEMP_COMPOSE_FILE.remove_service(new_container.name)
    TEMP_COMPOSE_FILE.write_to_file()

    return return_message

def _test_new_container(thread:thread_wrapper, new_container:service):
    docker = DockerClient(compose_files=(TEMP_COMPOSE_PATH))

    # check to see if the container builds
    try:
        docker.compose.build(services=(new_container.name), quiet=True)
    except DockerException as e:
        return _generate_return_msg(True, sub(DOCKER_AI_MSG_REG, '', f"Container failed to build -> Check your settings\nError was: {e}", flags=DOTALL))

    # check the install/seed script
    if (not _has_been_initialized(new_container.name)):
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

    # check to see if the actual launch function runs
    docker.compose.up(services=(new_container.name), quiet=True, detach=True)

    sleep(10)

    docker.stop(new_container.name+"_server", time=30)

    container = docker.container.inspect(new_container.name+"_server")
    exit_code = container.state.exit_code

    if exit_code != 0:
        return _generate_return_msg(True, f"Container failed to run -> Check your launch command\nLast 10 log lines were:\n{docker.logs(new_container.name+"_server", tail=10)}")

    docker.compose.down(services=(new_container.name), quiet=True)

    #MAIN_COMPOSE_FILE.add_service(new_container)
    #MAIN_COMPOSE_FILE.write_to_file()

    return _generate_return_msg(False)

def _generate_return_msg(failure:bool, message:str=None):
    return {
        "code": Server_codes.CONTAINER_FAILED if failure else Server_codes.CONTAINER_SUCCESS,
        "data": {'msg': message, 'success': not failure}
    }

def _has_been_initialized(server_name):
    return Path(SERVER_DATA_FILE_PATH, server_name).is_dir() and Path(SERVER_DATA_FILE_PATH, server_name, ".initialized").is_file()