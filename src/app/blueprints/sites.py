from flask_smorest import Blueprint
from flask.views import MethodView
from flask import render_template, make_response, session, redirect
from marshmallow import Schema, fields

from src.app.lib import SEND_SOCKET_THREAD, get_next_id, DATA_HANDLER
from src.lib import Server_codes, request
from ..lib import limiter, get_user_ip

from src.db.mappings import servers_view, container, launch_opts_view
from src.db.db import SessionLocal
from sqlalchemy import select

from pathlib import Path

MAX_ATTEMPTS = 3
ATTEMPT_TIME_DELTA = 10 # minutes

OVERVIEW_TYPES = ["cpu", "ram"]
ALL_GRAPH_TYPES = ["cpu", "ram", "upload", "download"]
IMAGE_FOLDER_PATH = "/src/app/static/images/"

blp = Blueprint("Sites", __name__)

class LoginSchema(Schema):
    username=fields.String(required=True)
    password=fields.String(required=True)

class AdminRedirectSchema(Schema):
    site=fields.String(required=True)

@blp.route("/")
class Front_Page(MethodView):
    def get(self):
        session["username"] = None
        session["password"] = None

        if session.get("session_id", None) == None:
            session["session_id"] = get_next_id()

        all_servers = _get_all_servers()
        launch_opts = _get_launch_opts()

        files = DATA_HANDLER.get_copy("files")
        print(launch_opts, flush=True)
        for file in files:
            launch_opts[file["s_name"]][file["lom_name"]] = file["files"]

        html = render_template("index.html", server_names=all_servers, launch_opts=launch_opts, image_mapping=_get_image_extensions())
        return make_response(html, 200)

@blp.route("/admin")
class Admin_Login(MethodView):
    def get(self):
        html = render_template("admin/login.html")
        return make_response(html, 200)
    
    @blp.response(200)
    @blp.response(405)
    @blp.arguments(LoginSchema, location="form")
    @limiter.limit("5 per minute")
    def post(self, form):
        # verify the user with the backend
        packet = SEND_SOCKET_THREAD.send_recv(request(None, {"username":form["username"], "password": form["password"], "ip": get_user_ip()}, Server_codes.CHECK_CREDENTIALS))

        if not packet: return make_response("Something went wrong", 404)
        if (packet.code != Server_codes.CREDENTIALS_OK):
            session.pop("username", None)
            session.pop("password", None)
            return make_response("You dont have access", 405)

        session["username"] = form["username"]
        session["password"] = form["password"]

        return redirect("admin/overview")

@blp.route("/admin/<string:site>")
class Admin_Page(MethodView):
    @blp.response(200)
    @blp.response(302)
    @blp.response(404)
    @blp.response(405)
    @limiter.exempt
    def get(self, site):
        login_confirmed = confirm_api_login()

        if login_confirmed == None: return make_response("Something went wrong", 404)

        if (login_confirmed == False):
            session.pop("username", None)
            session.pop("password", None)
            return make_response("You dont have access", 405)

        if (session.get("session_id", None) == None):
            session["session_id"] = get_next_id() 

        SEND_SOCKET_THREAD.send(request(None, {"id":session["session_id"]}, Server_codes.STOP_LOG_CONTAINER))

        match site:
            case "logout":
                session.pop("username", None)
                session.pop("password", None)

                return redirect("/")
            
            case "overview":
                all_servers = _get_all_servers()
                html = render_template(f'admin/overview/index.html', server_names=all_servers, types=OVERVIEW_TYPES, image_mapping=_get_image_extensions())
                return make_response(html, 200)
            
            case _:
                html = render_template(f'admin/{site}/index.html')

                return make_response(html, 200)
        
@blp.route("/admin/overview/<string:site>")
class Admin_Individual_Overview(MethodView):
    @blp.response(200)
    @blp.response(404)
    @blp.response(405)
    @limiter.exempt
    def get(self, site):
        login_confirmed = confirm_api_login()

        if login_confirmed == False: return make_response("You dont have access", 405)
        if login_confirmed == None: return make_response("Something went wrong", 404)

        query = select(servers_view.host_port).where(servers_view.name == site)

        with SessionLocal() as session:
            rows = session.execute(query).mappings().all()

        ports = []

        for row in rows:
            ports.append(row["host_port"])

        all_extensions = _get_image_extensions()

        extension = all_extensions[site] if site in all_extensions else "jpg"

        html = render_template("admin/overview/individual.html", server_name=site, types=ALL_GRAPH_TYPES, ports=ports, extension=extension)
        return make_response(html, 200)

@blp.route("/admin/help")
class Help_Site(MethodView):
    @blp.response(200)
    def get(self):
        html = render_template("admin/setup_help.html")
        return make_response(html, 200)
    
def confirm_api_login():
    if (not ("username" in session) or not ("password" in session)): return False

    username = session["username"]
    password = session["password"]

    packet = SEND_SOCKET_THREAD.send_recv(request(None, {"username":username, "password": password, "ip": get_user_ip()}, Server_codes.CHECK_REPEATED_CREDENTIALS))

    if (not packet): return None

    return packet.code == Server_codes.CREDENTIALS_OK

def _get_image_extensions():
    image_mapping = {}
    files = [f.name for f in Path(IMAGE_FOLDER_PATH).iterdir() if f.is_file()]

    for file in files:
        split_name = file.split(".")
        image_mapping[split_name[0]] = split_name[1]

    return image_mapping

def _get_all_servers():
    all_servers = []

    with SessionLocal() as db_session:
        rows = db_session.execute(select(container.name)).mappings().all()

        all_servers = [row["name"] for row in rows]

    return all_servers

def _get_launch_opts():
    launch_opts = {}

    with SessionLocal() as db_session:

        rows = db_session.execute(select(launch_opts_view.s_name, launch_opts_view.lom_name, launch_opts_view.lo_name)).mappings().all()
        
        for row in rows:
            if not (row.s_name in launch_opts):
                launch_opts[row.s_name] = {}

            if not (row.lom_name in launch_opts[row.s_name]):
                launch_opts[row.s_name][row.lom_name] = []

            launch_opts[row.s_name][row.lom_name].append(row.lo_name)

    return launch_opts