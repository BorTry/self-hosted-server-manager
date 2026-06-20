from flask_smorest import Blueprint
from flask.views import MethodView
from flask import make_response, Response, session, current_app

from src.app.lib import SOCKET_THREAD, DATA_HANDLER, add_subscriber, METRICS_INTERVAL
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

        ordered_rows = _order_rows(rows)

        for name in SOCKET_THREAD["all_servers"]:
            if name in ordered_rows: continue

            _fill_empty_rows(ordered_rows, name)

        ordered_rows["time_between"] = METRICS_INTERVAL

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
            metrics_view.upload,
            metrics_view.download
            ) \
            .where(
                metrics_view.time >= last_2_hours,
                metrics_view.name == server_name) \
            .order_by(metrics_view.time.desc()) \
            .limit(50)
    
        with SessionLocal() as session:
            rows = session.execute(query).mappings().all()

        ordered_rows = _order_rows(rows) if len(rows) > 1 else _fill_empty_rows({}, server_name)
        ordered_rows["time_between"] = METRICS_INTERVAL

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

def _fill_empty_rows(obj, entry_name):
    obj[entry_name] = [{
            "ram": 0,
            "cpu": 0,
            "time": datetime.now() - timedelta(seconds=METRICS_INTERVAL*2),
            "upload": 0,
            "download": 0
        },
        {
            "ram": 0,
            "cpu": 0,
            "time": datetime.now(),
            "upload": 0,
            "download": 0
        } 
    ]

    return obj

def _order_rows(ordered_arr):
    ordered_dict = {}

    for entry in ordered_arr:
        if not (entry.name in ordered_dict):
            ordered_dict[entry.name] = []

        entry_dict = {
            "time": entry.time,
            "cpu": entry.cpu,
            "ram": entry.ram
        }

        if hasattr(entry, "upload"):
            entry_dict["upload"] = entry.upload
            entry_dict["download"] = entry.download

        ordered_dict[entry.name].append(entry_dict)
    
    return ordered_dict