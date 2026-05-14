from flask_smorest import Blueprint
from flask.views import MethodView
from flask import render_template, make_response, session, redirect
from marshmallow import Schema, fields

from src.app.lib.constants import CREDENTIALS

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
    def post(self, form):
        username = form["username"]
        password = form["password"]

        if (password != CREDENTIALS["admin_password"] or username != CREDENTIALS["admin_username"]): return make_response("You dont have access", 405)

        session["username"] = username
        session["password"] = password

        return redirect("admin/overview")

@blp.route("/admin/<string:site>")
class admin_page(MethodView):
    @blp.response(200)
    @blp.response(404)
    @blp.response(405)
    def get(self, site):
        if (not ("username" in session) or not ("password" in session)): return make_response("You dont have access", 405)
        
        username = session["username"]
        password = session["password"]

        if (password != CREDENTIALS["admin_password"] or username != CREDENTIALS["admin_username"]): return make_response("You dont have access", 405)

        if site == "logout":
            username = None
            password = None

            return redirect("/")
        
        else:
            html = render_template(f'admin/{site}.html')
            return make_response(html, 200)