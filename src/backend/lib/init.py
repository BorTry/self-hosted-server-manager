from json import load, dumps
from platform import system
from os import path

from src.lib import CONSTANTS

CONFIG_FILE_PATH = path.abspath("./resources/config.json")
SERVER_JSON_FILE_PATH = "./servers.json"

# initialize the reverse container name to server name
def initialize_servers_json():
    json_servers = {}
    
    with open(SERVER_JSON_FILE_PATH, "r") as file:
        json_servers = load(file)

    all_servers = json_servers["server_names"]

    json_servers["container_to_server_names"] = {}    
    json_servers["server_names_to_container"] = {} 

    for server_name in all_servers:
        container_name = convert_to_container_name(server_name)

        json_servers["server_names_to_container"][server_name] = container_name
        json_servers["container_to_server_names"][container_name] = server_name

    with open(SERVER_JSON_FILE_PATH, "w") as file:
        file.write(dumps(json_servers, indent=4))

def convert_to_container_name(server_name:str):
    return server_name.replace(" ", "_").lower()

def fill_config():
    json_obj = None

    with open(CONFIG_FILE_PATH, "r") as file:
        json_obj = load(file)

    if (not json_obj):
        raise Exception("Something went wrong while opening config file")

    json_obj["os"] = system()

    CONSTANTS.START_IN_TUI = json_obj["start_in_tui"]
    CONSTANTS.OS = json_obj["os"]

    with open(CONFIG_FILE_PATH, "w") as file:
        file.write(dumps(json_obj, indent=4))

def init():
    initialize_servers_json()
    fill_config()