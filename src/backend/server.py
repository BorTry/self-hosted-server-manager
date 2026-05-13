from threading import Event
from src.backend.lib import socket_func, docker_func, docker_init, stop_frontend, start_frontend, docker_running, init
from src.lib import thread_wrapper, threads_socket_wrapper, threading_data_handler

init()

DATA = threading_data_handler({
        "data":[],
        "requests": []
    })

thread_terminate_event = Event()

DOCKER_THREAD = thread_wrapper(
    target=docker_func,
    init=docker_init,
    terminate_signal=thread_terminate_event,
    name="docker_thread",
    data_handler=DATA,
    sleep_time=0.5
) # Talks to the docker engine

PORT = 2024
ADDRESS = "0.0.0.0"

SOCKET_THREAD = threads_socket_wrapper(
    target=socket_func,
    address=(ADDRESS, PORT),
    terminate_signal=thread_terminate_event,
    data_handler=DATA,
    name="socket_thread"
) # Talks to the frontend

# The docker thread must be started before the com thread

def start_servers():
    print("============== Starting servers ==============")
    global DOCKER_THREAD, SOCKET_THREAD, thread_terminate_event

    DOCKER_THREAD.run()
    SOCKET_THREAD.run()

    start_frontend()

def stop_servers():
    print("============== Stopping servers ==============")
    global DOCKER_THREAD, SOCKET_THREAD, thread_terminate_event

    thread_terminate_event.set()

    stop_frontend()

    DOCKER_THREAD.terminate()
    SOCKET_THREAD.terminate()

def restart_servers():
    global DOCKER_THREAD, SOCKET_THREAD, thread_terminate_event

    stop_servers()

    if thread_terminate_event.is_set():
        thread_terminate_event.clear()

    # Get new instances of each thread
    DOCKER_THREAD = DOCKER_THREAD.get_new_instance()
    SOCKET_THREAD = SOCKET_THREAD.get_new_instance()

    start_servers()

def main():
    if (not docker_running()):
        raise Exception("Docker is not running")

    start_servers()

    while True:
        try:
            user_in = input("Select Action: \n")

            if (user_in == "quit" or user_in == "q"):
                break
            elif (user_in == "restart" or user_in == "r"):
                restart_servers()

        except Exception as e:
            print(e)

    stop_servers()

if __name__ == "__main__":
    main()