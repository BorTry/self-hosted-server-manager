from flask_smorest import Blueprint
from flask.views import MethodView
from flask import render_template, make_response
from marshmallow import Schema, fields

from src.app.constants import CREDENTIALS

blp = Blueprint("Sites", __name__)

class LoginSchema(Schema):
    username=fields.String()
    password=fields.String()

@blp.route("/")
class front_page(MethodView):
    def get(self):
        html = render_template("index.html")
        return make_response(html, 200)

@blp.route("/admin")
class admin_login(MethodView):
    def get(self):
        html = render_template("admin_login.html")
        return make_response(html, 200)
    
    @blp.response(200)
    @blp.response(405)
    @blp.arguments(LoginSchema, location="form") # TODO: Add protection against brute force attacks
    def post(self, form):
        username = form["username"]
        password = form["password"]

        if (password != CREDENTIALS["admin_password"] or username != CREDENTIALS["admin_username"]): return make_response(405)

        html = render_template("admin_page.html")
        return make_response(html, 200)