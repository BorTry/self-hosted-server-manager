from src.lib import thread_socket_wrapper
from src.app.lib.socket_functions import socket_func, socket_init

from time import sleep

ADDRESS = "0.0.0.0"
OWN_PORT = 2024
TARGET_ADDRESS = "host.docker.internal"
TARGET_PORT = 3024

SOCKET_THREAD = thread_socket_wrapper(
    target=socket_func,
    init=socket_init,
    address=(ADDRESS, OWN_PORT),
    target_address=(TARGET_ADDRESS, TARGET_PORT),
    name="app_socket_thread",
    sleeptime=2,
)

try:
    SOCKET_THREAD.run()
except OSError as e:
    print(e)

while (not SOCKET_THREAD.return_val):
    sleep(0.5)
    
ALL_SERVERS = SOCKET_THREAD.return_val
SOCKET_THREAD.return_val = None