from src.lib import thread_wrapper, Server_codes, response

from datetime import datetime, timedelta
from python_on_whales import docker
from pathlib import Path
from time import sleep

from json import dumps

DELTA_TIME = timedelta(seconds=5)
SERVER_DATA_FILE_PATH = Path(Path(__file__).resolve().parents[5], "server_data")

LIMITS = {
    "cpu": 3,
    "ram": 3,
    "disk": 5,
    "logs": 0,
} # percentage change allowed

MAX_ITERATIONS = 10

def check_run_command(thread:thread_wrapper, container_name:str):
    prev_state = None
    last_check = None
    iterations = 0

    thread.print(f"Starting testing of {container_name}")

    while MAX_ITERATIONS >= iterations and not thread.terminate_signal.is_set():
        container = docker.container.inspect(_convert_name(container_name))

        if not container.state.running: return False

        current_state = _get_current_state(container_name, last_check)
        last_check = datetime.now()

        if prev_state is None:
            prev_state = current_state
            sleep(DELTA_TIME.seconds)
            continue

        container_done = True

        for metric in LIMITS:
            current_allowed = LIMITS[metric]

            max_val = max(1, max(prev_state[metric], current_state[metric]))
            min_val = max(1, min(prev_state[metric], current_state[metric]))

            value = ((1 - (min_val / max_val)) * 100)

            if (value <= current_allowed): continue

            container_done = False
            break

        if (container_done): return True

        prev_state = current_state
        iterations += 1
        sleep(DELTA_TIME.seconds)

    thread.print("Time limit reached, not passed")
    return False

def _get_current_state(container_name:str, last_check:datetime|None):
    c_container_name = _convert_name(container_name)

    stats = docker.stats(c_container_name)[0]
    logs = len(docker.container.logs(c_container_name, since=None if last_check is None else last_check - DELTA_TIME))

    return {
        "ram": stats.memory_percentage,
        "cpu": stats.cpu_percentage,
        "disk": _get_folder_size(Path(SERVER_DATA_FILE_PATH, container_name)),
        "logs": logs
    }

def _get_folder_size(folder_path):
    root = Path(folder_path)
    # Sum the size of every item that is verified as a file
    return sum(f.stat().st_size for f in root.rglob('*') if f.is_file())

def _convert_name(name:str):
    return f"{name}_server"