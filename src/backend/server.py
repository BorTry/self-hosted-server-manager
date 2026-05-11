from threading import Event
from multiprocessing import Pipe
from time import sleep

from src.backend.lib.init import init
init()

from src.lib.ez_thread import ez_thread
from src.lib.sock_thread import sock_thread
from src.backend.lib.comm_thread import comm_func, comm_init, socket_func
from src.backend.lib.docker_thread import docker_func, docker_init
from src.backend.lib.docker_functions import stop_frontend, start_frontend, docker_running

thread_pipe_1, thread_pipe_2 = Pipe(duplex=True)
thread_terminate_event = Event()

COMMMUNICATION_THREAD = ez_thread(
    target=comm_func,
    init=comm_init,
    terminate_signal=thread_terminate_event,
    name="comm_thread",
    pipe=thread_pipe_1,
) # Facilitates communication between the two threads

DOCKER_THREAD = ez_thread(
    target=docker_func,
    init=docker_init,
    terminate_signal=thread_terminate_event,
    name="docker_thread",
    pipe=thread_pipe_2,
    sleep_time=0.5
) # Talks to the docker engine

PORT = 2024
ADDRESS = "0.0.0.0"

SOCKET_THREAD = sock_thread(
    target=socket_func,
    address=(ADDRESS, PORT),
    terminate_signal=thread_terminate_event,
    name="socket_thread"
) # Talks to the frontend

# The docker thread must be started before the com thread

def start_servers():
    print("============== Starting servers ==============")
    global DOCKER_THREAD, COMMMUNICATION_THREAD, SOCKET_THREAD, thread_terminate_event

    DOCKER_THREAD.run()
    COMMMUNICATION_THREAD.run()
    SOCKET_THREAD.run()

    start_frontend()

def stop_servers():
    print("============== Stopping servers ==============")
    global DOCKER_THREAD, COMMMUNICATION_THREAD, SOCKET_THREAD, thread_terminate_event

    thread_terminate_event.set()

    stop_frontend()

    DOCKER_THREAD.terminate()
    COMMMUNICATION_THREAD.terminate()
    SOCKET_THREAD.terminate()

def restart_servers():
    global DOCKER_THREAD, COMMMUNICATION_THREAD, SOCKET_THREAD, thread_terminate_event

    stop_servers()

    if thread_terminate_event.is_set():
        thread_terminate_event.clear()

    # Create a new pipe for communication
    thread_pipe_1, thread_pipe_2 = Pipe(duplex=True)

    # Get new instances of each thread
    DOCKER_THREAD = DOCKER_THREAD.get_new_instance(thread_pipe_2)
    COMMMUNICATION_THREAD = COMMMUNICATION_THREAD.get_new_instance(thread_pipe_1)
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