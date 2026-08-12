from threading import Event
from time import sleep

from src.backend.lib import *

from src.lib import thread_wrapper, thread_socket_wrapper, thread_data_handler
from src.lib.init import init
from src.lib.logger import logger, get_logger

init()

LOGGER = get_logger("main_thread")

DATA = thread_data_handler({
    "data":{
        "running_servers": [],
        "all_defined_servers": {}
    },
    "supervisor": {
        "requests": [],
        "responses": []
    },
    "creator": {
        "requests": [],
        "responses": []
    },
    "handler": {
        "requests": [],
        "responses": []
    },
})

thread_terminate_event = Event()

# =================== LOGGER ===================

LOGGER_THREAD = thread_wrapper(
    target=logger.print_all, 
    terminate_signal=thread_terminate_event, 
    name="log_thread", 
    sleep_time=.5
)

# =================== DOCKER THREADS ===================

DOCKER_SUPERVISOR_THREAD = thread_wrapper(
    target=docker_supervisor_func,
    init=docker_supervisor_init,
    on_close=docker_supervisor_on_close,
    terminate_signal=thread_terminate_event,
    name="docker_supervisor_thread",
    data_handler=DATA,
    sleep_time=0.5
)

DOCKER_CREATOR_THREAD = thread_wrapper(
    target=docker_creator_func,
    init=docker_creator_init,
    terminate_signal=thread_terminate_event,
    name="docker_creator_thread",
    data_handler=DATA.get_subsection("creator"),
    sleep_time=0.5
)

DOCKER_THREAD_HANDLER = thread_wrapper(
    target=docker_handler_func,
    init=docker_handler_init,
    terminate_signal=thread_terminate_event,
    name="docker_handler_thread",
    data_handler=DATA.get_subsection("handler"),
    sleep_time=0.5
)

# =================== SOCKET THREAD ===================

PORT = 3024
ADDRESS = "0.0.0.0"
CONTAINER_PORT = 2024

SOCKET_THREAD = thread_socket_wrapper(
    target=socket_func,
    init=socket_init,
    address=(ADDRESS, PORT),
    target_address=("localhost", 2024),
    terminate_signal=thread_terminate_event,
    data_handler=DATA,
    name="main_socket_thread",
    sleep_time=0.1
)

ALL_THREADS = [
    DOCKER_THREAD_HANDLER,
    DOCKER_CREATOR_THREAD,
    DOCKER_SUPERVISOR_THREAD,
    SOCKET_THREAD,
    LOGGER_THREAD,
]


def start_servers():
    print("\n============== Starting servers ==============\n\n")

    for thread_instance in ALL_THREADS:
        thread_instance.run()
    
    start_frontend()

def stop_servers():
    print("\n============== Stopping servers ==============\n\n")

    for thread_instance in ALL_THREADS:
        thread_instance.terminate()

    stop_frontend()

def restart_servers():
    stop_servers()

    if thread_terminate_event.is_set():
        thread_terminate_event.clear()

    for index in range(len(ALL_THREADS)):
        ALL_THREADS[index] = ALL_THREADS[index].get_new_instance()

    start_servers()

def main():
    if (not docker_running()):
        raise Exception("Docker is not running")

    start_servers()
    LOGGER.print("Server has been started")

    while True:
        try:
            user_in = input("")
            if (user_in == "quit" or user_in == "q"):
                break
            elif (user_in == "restart" or user_in == "r"):
                restart_servers()
            else: 
                print(f'There is no option for {user_in}. Use h for commands')

        except Exception as e:
            print(e)

    stop_servers()

if __name__ == "__main__":
    main()