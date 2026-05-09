from src.lib.sock_thread import sock_thread
from src.app.lib.socket_functions import socket_func, socket_init

ADDRESS = "0.0.0.0"
TARGET_ADDRESS = "host.docker.internal"
PORT = 2024

SOCKET_THREAD = sock_thread(
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