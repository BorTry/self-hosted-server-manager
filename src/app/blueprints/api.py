from flask_smorest import Blueprint
from flask.views import MethodView
from marshmallow import Schema, fields, ValidationError
from flask import jsonify

from src.app.constants import SOCKET_THREAD, ALL_SERVERS
from src.lib.server_codes import Server_codes


def get_running_servers():
    return SOCKET_THREAD.return_val



# ======================== SCHEMA ========================

blp = Blueprint("Containers", __name__, url_prefix="/api/container")

class ContainerResponseSchema(Schema):
    containers=fields.List(fields.Dict())

class ContainerStartSchema(Schema):
    name=fields.Str(required=True),
    launch_opts=fields.Dict(keys=fields.Str(), values=fields.Str())

# ======================== BLUEPRINTS ========================

@blp.route("/<int:id>")
class Container(MethodView):
    @blp.response(204)
    def get(self, id):
        # Get a single server
        # Talk to the backend to get it
        return jsonify(message=get_running_servers()[id])

    @blp.response(204)
    @blp.response(404)
    @blp.arguments(ContainerStartSchema)
    def post(self, form):    
        code = Server_codes.START_SERVER if form.pop("state") == "start" else Server_codes.STOP_SERVER

        SOCKET_THREAD.send(form, code)
        # Start up a server
        # Talk to the backend to start it
        pass


@blp.route("/all")
class AllContainers(MethodView):
    @blp.response(204, ContainerResponseSchema)
    @blp.response(404, Schema)
    def get(self):
        # Get all running servers
        return jsonify(message=ALL_SERVERS)


@blp.route("/all/running")
class AllContainers(MethodView):
    @blp.response(204, ContainerResponseSchema)
    @blp.response(404, Schema)
    def get(self):
        # Get all running servers
        return jsonify(message=get_running_servers())