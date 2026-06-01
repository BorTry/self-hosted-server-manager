from flask_smorest import Blueprint
from flask.views import MethodView
from marshmallow import Schema, fields
from flask import jsonify

from src.app.lib import SOCKET_THREAD, ALL_SERVERS
from src.lib import Server_codes
from ..lib.limiter import limiter

from src.db.db import SessionLocal
from src.db.mappings import performance_metric, traffic_metric, container, metric_timestamp
from sqlalchemy import select

from datetime import timedelta, datetime, timezone

def get_running_servers():
    return SOCKET_THREAD.return_val

# ======================== SCHEMA ========================

blp = Blueprint("Containers", __name__, url_prefix="/api")

class ContainerResponseSchema(Schema):
    containers=fields.List(fields.Dict())

class ContainerStartSchema(Schema):
    launch_opts=fields.Dict(keys=fields.Str(), values=fields.Str())

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
    
# ======================== ADMIN ========================

@blp.route("container/performance_metrics")
class AllContainerMetrics(MethodView):
    @blp.response(404)
    @blp.response(200)
    @limiter.exempt
    def get(self):
        ordered_rows = {}
        curr_date = datetime.now(timezone.utc) - timedelta(hours=2)

        with SessionLocal() as session:
            for server_name in ALL_SERVERS["servers"]:
                query = select(performance_metric.ram, performance_metric.cpu, metric_timestamp.time, container.name) \
                    .select_from(performance_metric) \
                    .join(container) \
                    .join(metric_timestamp) \
                    .where(
                        metric_timestamp.time >= curr_date,
                        container.name == server_name) \
                    .order_by(container.name.asc(), metric_timestamp.time.desc()) \
                    .limit(50)

                rows = session.execute(query).mappings().all()
                ordered_rows[server_name] = rows

        order_rows(ordered_rows)

        for row_name in ordered_rows:
            ordered_rows[row_name].sort(key=lambda x: x["time"])

        ordered_rows["time_between"] = "4"

        return ordered_rows

@blp.route("container/performance_metrics/<string:name>")
class AllContainerMetrics(MethodView):
    @limiter.exempt
    def get(self, name:str):
        ordered_rows = {}
        curr_date = datetime.now(timezone.utc) - timedelta(hours=2)
        
        with SessionLocal() as session:
            query = select(performance_metric.ram, performance_metric.cpu, metric_timestamp.time, container.name) \
                .select_from(performance_metric) \
                .join(container) \
                .join(metric_timestamp) \
                .where(
                    metric_timestamp.time >= curr_date,
                    container.name == name) \
                .order_by(metric_timestamp.time.desc()) \
                .limit(50)

            rows = session.execute(query).mappings().all()
            ordered_rows[name] = rows

        order_rows(ordered_rows)

        for row_name in ordered_rows:
            ordered_rows[row_name].sort(key=lambda x: x["time"])

        ordered_rows["time_between"] = "4"

        return ordered_rows[name]
    
def order_rows(ordered_rows):
    for row_name in ordered_rows:
        if (len(ordered_rows[row_name]) <= 1):
            ordered_rows[row_name] = [{
                    "ram": 0,
                    "cpu": 0,
                    "time": datetime.now() - timedelta(hours=1)
                },
                {
                    "ram": 0,
                    "cpu": 0,
                    "time": datetime.now()
                } 
            ]

            continue

        tmp = []
        for sub_row in ordered_rows[row_name]:
            tmp.append({
                "ram": sub_row["ram"],
                "cpu": sub_row["cpu"],
                "time": sub_row["time"]
            })

        ordered_rows[row_name] = tmp