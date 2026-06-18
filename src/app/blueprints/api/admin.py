from flask_smorest import Blueprint
from flask.views import MethodView
from flask import make_response, Response, session, current_app

from src.app.lib import SOCKET_THREAD, DATA_HANDLER, add_subscriber
from ...lib.limiter import limiter
from src.lib import Server_codes, request

from src.db.db import SessionLocal
from src.db.mappings import metrics_view
from sqlalchemy import select, func

from ..schemas import ContainerAddSchema, ContainerImage

from werkzeug.utils import secure_filename
from datetime import timedelta, datetime, timezone

blp = Blueprint("Admin_api", __name__, url_prefix="/api/admin")

@blp.route("/metrics")
class AllContainerMetrics(MethodView):
    @blp.response(404)
    @blp.response(200)
    @limiter.exempt
    def get(self):
        ordered_rows = {}
        last_2_hours = datetime.now(timezone.utc) - timedelta(hours=2)

        sub_query = select(
            metrics_view.name,
            metrics_view.time,
            metrics_view.cpu,
            metrics_view.ram,
            func.row_number()
                .over(
                    partition_by=metrics_view.name,
                    order_by=metrics_view.time.desc()
                )
                .label("rank_num")
        ) \
        .where(metrics_view.time >= last_2_hours) \
        .subquery()

        query = select(sub_query.c.name, sub_query.c.time, sub_query.c.cpu, sub_query.c.ram).where(sub_query.c.rank_num <= 50)

        with SessionLocal() as session:
            rows = session.execute(query).mappings().all()

        ordered_rows = order_rows(rows, True)

        ordered_rows["time_between"] = "4"

        return ordered_rows

@blp.route("/metrics/<string:server_name>")
class AllContainerMetrics(MethodView):
    @limiter.exempt
    def get(self, server_name:str):
        last_2_hours = datetime.now(timezone.utc) - timedelta(hours=2)

        query = select(
            metrics_view.name,
            metrics_view.time,
            metrics_view.cpu,
            metrics_view.ram,
            metrics_view.up,
            metrics_view.down
            ) \
            .where(
                metrics_view.time >= last_2_hours,
                metrics_view.name == server_name) \
            .order_by(metrics_view.time.desc()) \
            .limit(50)
    
        with SessionLocal() as session:
            rows = session.execute(query).mappings().all()

        ordered_rows = order_rows(rows)

        ordered_rows["time_between"] = "4"

        return ordered_rows

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

def order_rows(ordered_arr, add_empty_entries=False):
    ordered_dict = {}

    current_app.logger.info("allah oh akbar")
    current_app.logger.info(ordered_arr)

    for entry in ordered_arr:
        if not (entry.name in ordered_dict):
            ordered_dict[entry.name] = []

        entry_dict = {
            "time": entry.time,
            "cpu": entry.cpu,
            "ram": entry.ram
        }

        if hasattr(entry, "up"):
            entry_dict["up"] = entry.up
            entry_dict["down"] = entry.down

        ordered_dict[entry.name].append(entry_dict)

    if (not add_empty_entries): return ordered_dict

    for name in SOCKET_THREAD["all_servers"]:
        if name in ordered_dict: continue

        ordered_dict[name] = [{
                "ram": 0,
                "cpu": 0,
                "time": datetime.now() - timedelta(hours=2)
            },
            {
                "ram": 0,
                "cpu": 0,
                "time": datetime.now()
            } 
        ]

    return ordered_dict