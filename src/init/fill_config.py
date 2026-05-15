from json import load, dumps
from platform import system

from src.lib import CONSTANTS


def fill_config():
    json_obj = None

    with open(CONSTANTS.CONFIG_FILE_PATH, "r") as file:
        json_obj = load(file)

    if (not json_obj):
        raise Exception("Something went wrong while opening config file")

    json_obj["os"] = system()

    new_compose_hash = 

    CONSTANTS.START_IN_TUI = json_obj["start_in_tui"]
    CONSTANTS.OS = json_obj["os"]

    with open(CONSTANTS.CONFIG_FILE_PATH, "w") as file:
        file.write(dumps(json_obj, indent=4))