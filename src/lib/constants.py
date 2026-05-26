from os.path import abspath

class CONSTANTS:
    OS = None
    START_IN_TUI = None
    CONFIG_FILE_PATH = abspath("./resources/config.json")
    SERVER_JSON_FILE_PATH = abspath("./servers.json")
    COMPOSE_HASH = None
    CREDENTIALS = {
        "username": None,
        "password": None
    }
    METRICS_INTERVAL = 1