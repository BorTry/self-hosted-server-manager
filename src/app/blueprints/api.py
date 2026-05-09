from flask_smorest import Blueprint
from flask.views import MethodView
from marshmallow import Schema, fields, ValidationError

from src.app.constants import SOCKET_THREAD

blp = Blueprint("Containers", __name__, url_prefix="/api/container")

class ContainerResponseSchema(Schema):
    containers=fields.List(fields.Dict())

class ContainerStartSchema(Schema):
    name=fields.Str(required=True),
    launch_opts=fields.Dict(keys=fields.Str(), values=fields.Str())

@blp.route("/<id:int>")
class Container(MethodView):
    @blp.response(200, )
    def get(self, id):
        # Get a single server
        # Talk to the backend to get it
        pass

    @blp.response(200, Schema)
    @blp.response(404, Schema)
    @blp.arguments(ContainerStartSchema)
    def post(self, id):
        # Start up a server
        # Talk to the backend to start it
        pass

@blp.route("/all")
class AllContainers(MethodView):
    @blp.response(200, ContainerResponseSchema)
    @blp.response(404, Schema)
    def get(self):
        # Get all running servers
        pass