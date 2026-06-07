from flask_smorest import Blueprint
from flask.views import MethodView
from flask import make_response, Response, session

from src.app.lib import SOCKET_THREAD, DATA_HANDLER, add_subscriber
from ...lib.limiter import limiter
from src.lib import Server_codes, request

from src.db.db import SessionLocal
from src.db.mappings import performance_metric, traffic_metric, container, metric_timestamp
from sqlalchemy import select

from ..schemas import ContainerAddSchema, ContainerImage

from werkzeug.utils import secure_filename
from datetime import timedelta, datetime, timezone

blp = Blueprint("Admin_api", __name__, url_prefix="/api/admin")

@blp.route("performance_metrics")
class AllContainerMetrics(MethodView):
    @blp.response(404)
    @blp.response(200)
    @limiter.exempt
    def get(self):
        ordered_rows = {}
        curr_date = datetime.now(timezone.utc) - timedelta(hours=2)

        with SessionLocal() as session:
            for server_name in SOCKET_THREAD["all_servers"]:
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

@blp.route("performance_metrics/<string:name>")
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

@blp.route("add_container")
class addContainer(MethodView):
    @blp.arguments(ContainerAddSchema, location="form")
    @blp.arguments(ContainerImage, location="files")
    @limiter.exempt
    def post(self, form_data, files):
        session_id = session.get("session_id", None)

        if (session_id is None):
            return make_response("No session ID", 403)
    
        form_schema = ContainerAddSchema()
        image = files["image"]

        data = form_schema.dump(form_data)
        data["image_name"] = image.filename

        with DATA_HANDLER as thread_data:
            thread_data["pending_requests"].append(request(session["session_id"], data, Server_codes.ADD_CONTAINER))

        if image:
            filename = secure_filename(image.filename)
            save_path = "src/app/static/images/"+filename

            image.save(save_path)

        return make_response("", 200)

    @limiter.exempt
    def get(self):
        session_id = session.get("session_id", None)

        if (session_id == None): return make_response("", 500)

        queue = add_subscriber(SOCKET_THREAD, session_id)

        def stream():
            try:
                while True:
                    msg = queue.get()

                    yield "event: update\n"
                    yield f'data: {msg}\n\n'
            finally:
                queue.close()

        return Response(stream(), status=200, mimetype="text/event-stream")

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