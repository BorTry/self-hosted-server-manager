from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify

from src.app.lib import DATA_HANDLER, SEND_SOCKET_THREAD, add_request
from src.lib import Server_codes, request
from ...lib.limiter import limiter

from ..schemas import ContainerResponseSchema, ContainerStartSchema

def get_running_servers():
    return DATA_HANDLER.get_copy("running_servers")

blp = Blueprint("Frontend_api", __name__, url_prefix="/api")

@blp.route("container/<string:name>")
class Container(MethodView):
    @blp.response(204)
    def get(self, name:str):
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

        add_request(request(None, packet, Server_codes.START_SERVER))

        return "", 204

@blp.route("container/<string:name>/stop")
class Stop_Containers(MethodView):
    @blp.response(204)
    @blp.response(404)
    @limiter.limit("5 per minute")
    def post(self, name:str):    
        packet = {"name":name}   
        
        add_request(request(None, packet, Server_codes.STOP_SERVER))

        return "", 204

@blp.route("container/all")
class AllContainers(MethodView):
    @blp.response(204, ContainerResponseSchema)
    @blp.response(404)
    @limiter.exempt
    def get(self):
        return jsonify(message={
            "all_servers": SEND_SOCKET_THREAD["all_servers"],
            "launch_opts": SEND_SOCKET_THREAD["launch_options"]
        })

@blp.route("container/all/running")
class AllContainers(MethodView):
    @blp.response(204, ContainerResponseSchema)
    @blp.response(404)
    @limiter.exempt
    def get(self):
        return jsonify(message=get_running_servers())