from flask_smorest import Blueprint
from flask.views import MethodView
from flask import render_template, make_response, session, redirect, request
from marshmallow import Schema, fields
from sqlalchemy import select

from src.app.lib import SOCKET_THREAD
from src.lib import Server_codes
from ..lib import limiter, get_user_ip

from src.db.db import SessionLocal
from src.db.mappings import connections, login_attempts

from datetime import datetime, timedelta

MAX_ATTEMPTS = 3
ATTEMPT_TIME_DELTA = 10 # minutes

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
        
        html = render_template("index.html")
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
        packet = SOCKET_THREAD.send_recv(Server_codes.CHECK_CREDENTIALS, {"username":form["username"], "password": form["password"]})

        if (not verify_login(packet)):
            session.pop("username", None)
            session.pop("password", None)
            return  make_response("You dont have access", 405)

        session["username"] = form["username"]
        session["password"] = form["password"]

        return redirect("admin/overview")

@blp.route("/admin/<string:site>")
class admin_page(MethodView):
    @blp.response(200)
    @blp.response(302)
    @blp.response(404)
    @blp.response(405)
    def get(self, site):
        if (not ("username" in session) or not ("password" in session)): return make_response("You dont have access", 405)
        
        username = session["username"]
        password = session["password"]

        packet = SOCKET_THREAD.send_recv(Server_codes.CHECK_REPEATED_CREDENTIALS, {"username":username, "password": password})

        if (not verify_login(packet)):
            session.pop("username", None)
            session.pop("password", None)
            return make_response("You dont have access", 405)

        if site == "logout":
            session.pop("username", None)
            session.pop("password", None)

            return redirect("/")

        else:
            html = render_template(f'admin/{site}.html')
            return make_response(html, 200)
        

def get_ip_entry(s):
    request_ip = get_user_ip()
    ip_query = select(connections).where(connections.ip == request_ip)

    connection_entry = s.scalars(ip_query).first()

    if not connection_entry:
        connection_entry = connections(ip=request_ip)
        print("Creating new database entry")
        s.add(connection_entry)
        s.commit()

    return connection_entry

def get_login_attemps(entry, s):
    cutoff = datetime.now() - timedelta(minutes=ATTEMPT_TIME_DELTA)

    # check the amount of recent login attempts that failed
    login_attempts_query = select(login_attempts).where(
        login_attempts.connection_id == entry.id, 
        login_attempts.failed_login == True,
        login_attempts.time >= cutoff
    )
    return s.scalars(login_attempts_query).all()

def verify_login(packet):
    with SessionLocal() as s:
        connection_entry = get_ip_entry(s)
        
        if (connection_entry.blacklisted):
            return False

        attempts = get_login_attemps(connection_entry, s)

        if (len(attempts) >= MAX_ATTEMPTS):
            connection_entry.blacklisted = True
            s.commit()

            print(f'Blacklisting ip: {get_user_ip()}')
            return False

        new_login_entry = login_attempts(connection_id=connection_entry.id)
        s.add(new_login_entry)
        s.commit()

        if (packet["code"] != Server_codes.CREDENTIALS_OK): 
            return False
        
        new_login_entry.failed_login = False
        s.commit()

        return True