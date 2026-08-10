from threading import Event
from time import sleep

from src.backend.lib import socket_func, docker_func, docker_init, docker_on_close, stop_frontend, start_frontend, docker_running, socket_init
from src.lib import thread_wrapper, thread_socket_wrapper, thread_data_handler
from src.lib.init import init
from src.lib.logger import logger, get_logger

init()

LOGGER = get_logger("main_thread")

DATA = thread_data_handler({
        "data":[None for _ in range(10)],
        "requests": [],
        "responses": []
    })

thread_terminate_event = Event()

#TUI = TextualApp(data_handler=DATA)

LOGGER_THREAD = thread_wrapper(
    target=logger.print_all, 
    terminate_signal=thread_terminate_event, 
    name="log_thread", 
    sleep_time=.5
)

DOCKER_THREAD = thread_wrapper(
    target=docker_func,
    init=docker_init,
    on_close=docker_on_close,
    terminate_signal=thread_terminate_event,
    name="docker_thread",
    data_handler=DATA,
    sleep_time=0.5
) # Talks to the docker engine

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
    sleeptime=0.1
) # Talks to the frontend

def start_servers():
    print("\n============== Starting servers ==============\n\n")

    start_frontend()
    
    DOCKER_THREAD.run()
    SOCKET_THREAD.run()
    LOGGER_THREAD.run()

def stop_servers():
    print("\n============== Stopping servers ==============\n\n")

    thread_terminate_event.set()

    DOCKER_THREAD.terminate()
    SOCKET_THREAD.terminate()
    sleep(1)
    LOGGER_THREAD.terminate()

    stop_frontend()

def restart_servers():
    global DOCKER_THREAD, SOCKET_THREAD, LOGGER_THREAD, thread_terminate_event

    stop_servers()

    if thread_terminate_event.is_set():
        thread_terminate_event.clear()

    # Get new instances of each thread
    LOGGER_THREAD = LOGGER_THREAD.get_new_instance()
    DOCKER_THREAD = DOCKER_THREAD.get_new_instance()
    SOCKET_THREAD = SOCKET_THREAD.get_new_instance()

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