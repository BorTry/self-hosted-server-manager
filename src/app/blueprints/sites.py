from flask_smorest import Blueprint
from flask.views import MethodView
from flask import render_template, make_response, session, redirect
from marshmallow import Schema, fields

from src.app.lib import SEND_SOCKET_THREAD, get_next_id
from src.lib import Server_codes, request
from ..lib import limiter, get_user_ip

from src.db.mappings import servers_view
from src.db.db import SessionLocal
from sqlalchemy import select

MAX_ATTEMPTS = 3
ATTEMPT_TIME_DELTA = 10 # minutes

OVERVIEW_TYPES = ["cpu", "ram"]
ALL_GRAPH_TYPES = ["cpu", "ram", "upload", "download"]

blp = Blueprint("Sites", __name__)

class LoginSchema(Schema):
    username=fields.String(required=True)
    password=fields.String(required=True)

class AdminRedirectSchema(Schema):
    site=fields.String(required=True)

@blp.route("/")
class front_page(MethodView):
    def get(self):
        session["username"] = None
        session["password"] = None

        if session.get("session_id", None) == None:
            session["session_id"] = get_next_id()
        
        html = render_template("index.html", server_names=SEND_SOCKET_THREAD["all_servers"])
        return make_response(html, 200)

@blp.route("/admin")
class admin_login(MethodView):
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
class admin_page(MethodView):
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
                html = render_template(f'admin/{site}/index.html', server_names=SEND_SOCKET_THREAD["all_servers"], types=OVERVIEW_TYPES)
                return make_response(html, 200)
            
            case _:
                html = render_template(f'admin/{site}/index.html')

                return make_response(html, 200)
        
@blp.route("/admin/overview/<string:site>")
class admin_individual_overview(MethodView):
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

        html = render_template("admin/overview/individual.html", server_name=site, types=ALL_GRAPH_TYPES, ports=ports)
        return make_response(html, 200)

@blp.route("/admin/help")
class help_site(MethodView):
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