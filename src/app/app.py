from flask import Flask, render_template, jsonify, request

from src.lib.sock_thread import sock_thread
from src.lib.server_codes import *
from lib.socket_functions import socket_func, socket_init

# ======================= Socket code =======================

IS_IN_CONTAINER = True
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

# ======================= Server code =======================

app = Flask(__name__)

def get_running_servers():
    return SOCKET_THREAD.return_val

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/backend/server_count", methods=["GET"])
def backend_servercount():
    if (IS_IN_CONTAINER):
        data = get_running_servers()
        return jsonify(message=data), 200
    return jsonify(message=None), 404

@app.route("/backend/all_servers", methods=["GET"])
def backend_allservers():
    if (IS_IN_CONTAINER):
        return jsonify(message=ALL_SERVERS), 200
    return jsonify(message=None), 404

@app.route("/backend/all_running_servers", methods=["GET"])
def backend_all_running_servers():
    if (IS_IN_CONTAINER):
        data = get_running_servers()
        return jsonify(message=data), 200
    return jsonify(message=None), 404



@app.route("/backend/change_server", methods=["POST"])
def backend_start_up():
    if (IS_IN_CONTAINER):
        req_dict = request.form.to_dict()
        
        code = Server_codes.START_SERVER if req_dict.pop("state") == "start" else Server_codes.STOP_SERVER

        SOCKET_THREAD.send(req_dict, code)
        return jsonify(message=":)"), 200
    return jsonify(message=None), 404