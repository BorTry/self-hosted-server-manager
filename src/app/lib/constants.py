from dotenv import load_dotenv
from os import environ

load_dotenv("./.env")
METRICS_INTERVAL = int(environ.get("METRICS_INTERVAL"))

ADDRESS = "0.0.0.0"
OWN_PORT = 2024
TARGET_ADDRESS = "host.docker.internal"
TARGET_PORT = 3024