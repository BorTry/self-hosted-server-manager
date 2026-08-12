from src.lib import thread_wrapper, thread_socket_wrapper, Server_codes, CONSTANTS, response, thread_data_handler

from python_on_whales import docker
from datetime import datetime, timedelta

LOGGER_THREAD_SLEEP_TIME = 5
MAX_LOGGER_IDLE_TIME = 20 # measured in minutes

def logger_func(thread:thread_socket_wrapper):
    if not thread["full_logs"]:
        last_30_min = thread["last_check"] - timedelta(minutes=30)
        logs = docker.logs(container=thread["server_name"], since=last_30_min)
    else:
        logs = docker.logs(container=thread["server_name"], since=thread["last_check"])

    thread["last_check"] = datetime.now() - timedelta(seconds=1)

    global_session_ids = thread.data_handler.get_copy("session_ids")

    if (thread["last_log_time"] < (thread["last_check"] - timedelta(seconds=MAX_LOGGER_IDLE_TIME)) and len(global_session_ids) == 0):
        thread.print("Closing thread: No traffic")
        thread.terminate_next_cycle()
        return

    if not logs: return

    if (len(global_session_ids) > 0):
        thread["last_log_time"] = thread["last_check"]

    thread["full_logs"] += logs

    for session_id in global_session_ids:
        if not (session_id in thread["session_ids"]):
            thread.send(response(session_id, thread["full_logs"], Server_codes.LOG_CONTAINER))
        else:
            thread.send(response(session_id, logs, Server_codes.LOG_CONTAINER))

    thread["session_ids"] = global_session_ids

def logger_init(thread:thread_socket_wrapper):
    thread["full_logs"] = ""
    thread["last_check"] = datetime.now()
    thread["last_log_time"] = datetime.now()
    thread["session_ids"] = set()

def logger_generator(container_name:str):
    if container_name is None:
        raise Exception("Log thread needs a container name")

    data_handler = thread_data_handler(
        {"session_ids":set()}
    )

    log_thread = thread_socket_wrapper(
        target=logger_func,
        init=logger_init,
        data_handler=data_handler,
        target_address=("localhost", 2024),
        sleep_time=LOGGER_THREAD_SLEEP_TIME,
        name=f'log_thread_{container_name}'
    )

    log_thread["server_name"] = container_name

    log_thread.run()

    return log_thread

def add_session_id(thread:thread_socket_wrapper, session_id:int):
    if type(thread.data_handler) == str:
        print(thread.data_handler)
    
    with thread.data_handler as data:
        data["session_ids"].add(session_id)

def remove_session_id(thread:thread_wrapper, session_id:int):
    for logger_name in thread["logger_threads"]:
        logger = thread["logger_threads"][logger_name]

        with logger.data_handler as data:
            if session_id in data["session_ids"]:
                data["session_ids"].remove(session_id)