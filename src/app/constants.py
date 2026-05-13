from json import load
from os import path

from src.lib import threads_socket_wrapper
from src.app.lib.socket_functions import socket_func, socket_init

CONFIG_FILE = path.abspath("./resources/config.json")

CREDENTIALS = None

with open(CONFIG_FILE, "r") as file:
    config_dict = load(file)
    CREDENTIALS = {
        "admin_password" : config_dict["admin_password"],
        "admin_username" : config_dict["admin_username"]
    }

ADDRESS = "0.0.0.0"
TARGET_ADDRESS = "host.docker.internal"
PORT = 2024

SOCKET_THREAD = threads_socket_wrapper(
    target=socket_func,
    init=socket_init,
    address=(ADDRESS, PORT),
    target_address=(TARGET_ADDRESS, PORT),
    name="socket_thread",
    sleeptime=2,
)

SOCKET_THREAD.run()

ALL_SERVERS = SOCKET_THREAD.return_val
SOCKET_THREAD.return_val = None