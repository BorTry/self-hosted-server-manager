from src.lib import thread_wrapper, thread_socket_wrapper, Server_codes, CONSTANTS, response, thread_data_handler

from python_on_whales import docker
from datetime import datetime
from threading import Event

LOGGER_THREAD_SLEEP_TIME = 5

def logger_func(thread:thread_socket_wrapper):
    if not thread["full_logs"]:
        thread["full_logs"] = docker.logs(container=thread["server_name"])
        thread["last_check"] = datetime.now()
        return

    logs = docker.logs(container=thread["server_name"], since=thread["last_check"])
    thread["last_check"] = datetime.now()

    if not logs: return

    thread["full_logs"] += logs

    global_session_ids = thread.data_handler.get_copy("session_ids")

    for session_id in global_session_ids:
        if not (session_id in thread["session_ids"]):
            thread.send(response(session_id, {"logs":f'{thread["full_logs"]!r}'}, Server_codes.LOG_CONTAINER))
            thread["session_ids"].add(session_id)
        else:
            thread.send(response(session_id, {"logs":logs}, Server_codes.LOG_CONTAINER))

def logger_init(thread:thread_socket_wrapper):
    thread["full_logs"] = ""
    thread["last_check"] = datetime.now()
    thread["session_ids"] = set()

def logger_generator(container_name:str, terminate_signal:Event):
    if terminate_signal is None or type(terminate_signal) is not Event:
        raise Exception("Log thread needs a 'threading Event' as the terminate signal")

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
        sleeptime=LOGGER_THREAD_SLEEP_TIME,
        terminate_signal=terminate_signal,
        name=f'log_thread_{container_name}'
    )

    log_thread["server_name"] = container_name

    log_thread.run()

    return log_thread

def add_session_id(thread:thread_socket_wrapper, session_id:int):
    with thread.data_handler as data:
        data["session_ids"].add(session_id)

def remove_session_id(thread:thread_socket_wrapper, session_id:int):
    with thread.data_handler as data:
        if session_id in data["session_ids"]:
            data["session_ids"].remove(session_id)