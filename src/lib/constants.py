from os.path import abspath

class CONSTANTS:
    OS = None
    START_IN_TUI = None
    CONFIG_FILE_PATH = abspath("./resources/config.json")
    SERVER_JSON_FILE_PATH = abspath("./servers.json")
    CREDENTIALS = {
        "username": None,
        "password": None
    }
    METRICS_INTERVAL = None