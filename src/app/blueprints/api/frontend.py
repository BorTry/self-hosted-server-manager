from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify

from src.app.lib import SOCKET_THREAD, ALL_SERVERS
from src.lib import Server_codes
from ...lib.limiter import limiter

from ..schemas import ContainerResponseSchema, ContainerStartSchema

def get_running_servers():
    return SOCKET_THREAD.return_val

# ======================== SCHEMA ========================

blp = Blueprint("Frontend_api", __name__, url_prefix="/api")

# ======================== BLUEPRINTS ========================

@blp.route("container/<string:name>")
class Container(MethodView):
    @blp.response(204)
    def get(self, name:str):
        # Get a single server
        # Talk to the backend to get it
        return jsonify(message=get_running_servers()[name])

@blp.route("container/<string:name>/start")
class Start_Containers(MethodView):
    @blp.response(204)
    @blp.response(404)
    @blp.arguments(ContainerStartSchema)
    @limiter.limit("5 per minute")
    def post(self, form:ContainerStartSchema, name:str):
        packet = {
            "name":name, 
            "opt":form["launch_opts"] if "launch_opts" in form else "" 
        }
        SOCKET_THREAD.send(packet, Server_codes.START_SERVER)
        # Start up a server
        # Talk to the backend to start it
        return "", 204

@blp.route("container/<string:name>/stop")
class Stop_Containers(MethodView):
    @blp.response(204)
    @blp.response(404)
    @limiter.limit("5 per minute")
    def post(self, name:str):    
        packet = {"name":name}   
        SOCKET_THREAD.send(packet, Server_codes.STOP_SERVER)

        return "", 204
        # Stop a server
        # Talk to the backend to stop it

@blp.route("container/all")
class AllContainers(MethodView):
    @blp.response(204, ContainerResponseSchema)
    @blp.response(404)
    @limiter.exempt
    def get(self):
        # Get all running servers
        return jsonify(message=ALL_SERVERS)


@blp.route("container/all/running")
class AllContainers(MethodView):
    @blp.response(204, ContainerResponseSchema)
    @blp.response(404)
    @limiter.exempt
    def get(self):
        # Get all running servers
        return jsonify(message=get_running_servers())