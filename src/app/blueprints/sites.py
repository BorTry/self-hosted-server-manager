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
    @blp.arguments(LoginSchema, location="form") # TODO: Add protection against brute force attacks
    @limiter.limit("5 per minute")
    def post(self, form):
        # verify the user with the backend
        packet = SOCKET_THREAD.send_recv(Server_codes.CHECK_CREDENTIALS, {"username":form["username"], "password": form["password"]})

        with SessionLocal() as s:
            query = select(connections).where(connections.ip == get_user_ip())
            connection_entry = s.scalars(query).first()

            if not connection_entry:
                connection_entry = connections(ip=get_user_ip())
                print("Creating new database entry")
                s.add(connection_entry)
                s.commit()

            new_login_entry = login_attempts(connection_id=connection_entry.id)
            s.add(new_login_entry)

            if (packet["code"] != Server_codes.CREDENTIALS_OK): 
                s.commit()
                return make_response("You dont have access", 405)
            
            new_login_entry.failed_login = False
            s.commit()

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

        packet = SOCKET_THREAD.send_recv(Server_codes.CHECK_CREDENTIALS, {"username":username, "password": password})

        if (packet["code"] != Server_codes.CREDENTIALS_OK): return make_response("You dont have access", 405)

        if site == "logout":
            username = None
            password = None

            return redirect("/")
        
        else:
            html = render_template(f'admin/{site}.html')
            return make_response(html, 200)