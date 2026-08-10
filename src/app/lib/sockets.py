from src.lib import thread_socket_wrapper, thread_data_handler, thread_wrapper
from src.lib.logger import logger
from src.app.lib.sockets_functions.send_socket import send_socket_func, send_socket_init
from src.app.lib.sockets_functions.listen_socket import listen_socket_func, listen_socket_init

from .constants import ADDRESS, OWN_PORT, TARGET_ADDRESS, TARGET_PORT

from threading import Event
import atexit

TERMINATE_SIGNAL = Event()

DATA_HANDLER = thread_data_handler({
    "subscribers": {},
    "running_servers": {},
    "pending_requests": [],
    "current_id": 1
})

LOGGER_THREAD = thread_wrapper(
    target=logger.print_all, 
    name="log_thread", 
    terminate_signal=TERMINATE_SIGNAL,
    sleep_time=.5
)

SEND_SOCKET_THREAD = thread_socket_wrapper(
    target=send_socket_func,
    init=send_socket_init,
    target_address=(TARGET_ADDRESS, TARGET_PORT),
    terminate_signal=TERMINATE_SIGNAL,
    data_handler=DATA_HANDLER,
    name="app_send_socket_thread",
    sleep_time=2,
)

LISTEN_SOCKET_THREAD = thread_socket_wrapper(
    target=listen_socket_func,
    init=listen_socket_init,
    address=(ADDRESS, OWN_PORT),
    terminate_signal=TERMINATE_SIGNAL,
    data_handler=DATA_HANDLER,
    name="app_listen_socket_thread",
    sleep_time=1,
)

atexit.register(lambda _: TERMINATE_SIGNAL.set())

try:
    LOGGER_THREAD.run()
    LISTEN_SOCKET_THREAD.run()
    SEND_SOCKET_THREAD.run()
except OSError as e:
    print(e)