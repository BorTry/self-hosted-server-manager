from flask_smorest import Blueprint
from flask.views import MethodView
from marshmallow import Schema, fields
from flask import jsonify

from src.app.lib.constants import SOCKET_THREAD, ALL_SERVERS
from src.lib.server_codes import Server_codes

def get_running_servers():
    return SOCKET_THREAD.return_val

# ======================== SCHEMA ========================

blp = Blueprint("Containers", __name__, url_prefix="/api")

class ContainerResponseSchema(Schema):
    containers=fields.List(fields.Dict())

class ContainerStartSchema(Schema):
    #name=fields.Str(required=True),
    launch_opts=fields.Dict(keys=fields.Str(), values=fields.Str())

# ======================== BLUEPRINTS ========================

@blp.route("container/<string:name>")
class Container(MethodView):
    @blp.response(204)
    def get(self, name):
        # Get a single server
        # Talk to the backend to get it
        return jsonify(message=get_running_servers()[name])

@blp.route("container/<string:name>/start")
class Start_Containers(MethodView):
    @blp.response(204)
    @blp.response(404)
    @blp.arguments(ContainerStartSchema)
    def post(self, form, name):
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
    @blp.arguments(ContainerStartSchema)
    def post(self, form, name):    
        packet = {
            "name":name, 
            "opt":form["launch_opts"] if "launch_opts" in form else "" 
        }   
        SOCKET_THREAD.send(packet, Server_codes.STOP_SERVER)

        return "", 204
        # Stop a server
        # Talk to the backend to stop it


@blp.route("container/all")
class AllContainers(MethodView):
    @blp.response(204, ContainerResponseSchema)
    @blp.response(404, Schema)
    def get(self):
        # Get all running servers
        return jsonify(message=ALL_SERVERS)


@blp.route("container/all/running")
class AllContainers(MethodView):
    @blp.response(204, ContainerResponseSchema)
    @blp.response(404, Schema)
    def get(self):
        # Get all running servers
        return jsonify(message=get_running_servers())