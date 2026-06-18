from src.lib import thread_wrapper, compose_file, service

from python_on_whales import DockerClient, DockerException

TEMP_COMPOSE_PATH = "./resources/compose_files/docker-temp-compose.yaml"
MAIN_COMPOSE_PATH = "./resources/compose_files/docker-game-compose.yaml"

TEMP_COMPOSE_FILE = compose_file(TEMP_COMPOSE_PATH)
MAIN_COMPOSE_FILE = compose_file(MAIN_COMPOSE_PATH)

def try_to_add_container(thread:thread_wrapper, compose_args) -> bool:
    server_name = compose_args["server_name"]

    new_container = service(
        name=server_name,
        container_name=server_name+"_server",
        cpus=str(compose_args["cpu_limit"])+".0",
        mem_limit=compose_args["ram_limit"]+"GB",
        command=compose_args["launch_opt"],
        image="alpine",
        user="server_user:server_user",
        working_dir="/data",
    )

    # add dicts and arrays
    new_container["ports"] = compose_args["ports"].split(";")
    new_container["volumes"] = [f"${{SERVER_DATA_PATH}}/{server_name}:/data"]
    new_container["entrypoint"] = ["/entrypoint.sh"]

    if (False):
        new_container["build"] = {"context": "../buildfiles", "dockerfile": f"Dockerfile.{server_name}"}
    
    thread.print(new_container)

    TEMP_COMPOSE_FILE.add_service(new_container)
    TEMP_COMPOSE_FILE.write_to_file()

    _test_new_container(thread, new_container)

def _test_new_container(thread:thread_wrapper, new_container:service):
    docker = DockerClient(compose_files=(TEMP_COMPOSE_PATH))

    success = False

    try:
        docker.compose.build(services=(new_container.name), quiet=True)
        success = True
        thread.print("works")
    except DockerException as e:
        print(e)

    if not success:
        return False

    success = False

    try:
        docker.compose.up(services=(new_container.name), quiet=True)
        success = True
        thread.print("works 2")
    except DockerException as e:
        print(e)
    
    docker.compose.down(services=(new_container.name))
    TEMP_COMPOSE_FILE.remove_service(new_container.name)
    TEMP_COMPOSE_FILE.write_to_file()

    if not success:
        return False

    #MAIN_COMPOSE_FILE.add_service(new_container)
    #MAIN_COMPOSE_FILE.write_to_file()