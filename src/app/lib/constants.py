from src.lib import thread_socket_wrapper, thread_data_handler, thread_wrapper
from src.lib.logger import logger
from src.app.lib.socket_functions import socket_func, socket_init
from dotenv import load_dotenv
from os import environ

load_dotenv("./.env")
METRICS_INTERVAL = int(environ.get("METRICS_INTERVAL"))

ADDRESS = "0.0.0.0"
OWN_PORT = 2024
TARGET_ADDRESS = "host.docker.internal"
TARGET_PORT = 3024

DATA_HANDLER = thread_data_handler({
    "subscribers": {},
    "running_servers": [],
    "pending_requests": [],
    "current_id": 1
})

LOGGER_THREAD = thread_wrapper(
    target=logger.print_all, 
    name="log_thread", 
    sleep_time=.5
)

SOCKET_THREAD = thread_socket_wrapper(
    target=socket_func,
    init=socket_init,
    address=(ADDRESS, OWN_PORT),
    target_address=(TARGET_ADDRESS, TARGET_PORT),
    data_handler=DATA_HANDLER,
    name="app_socket_thread",
    sleeptime=2,
)

try:
    LOGGER_THREAD.run()
    SOCKET_THREAD.run()
except OSError as e:
    print(e)