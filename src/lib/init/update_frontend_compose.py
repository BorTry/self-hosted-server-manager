from ..constants import CONSTANTS
from ..parsers.docker import compose_file

FILE_PATH = "./resources/compose_files/docker-frontend-compose.yaml"

def update_frontend_environment_var():
    compose_struct = compose_file(FILE_PATH)

    compose_struct.services["frontend"]["environment"]["METRICS_INTERVAL"] = CONSTANTS.METRICS_INTERVAL

    compose_struct.write_to_file()