from flask_smorest import Blueprint
from flask.views import MethodView
from flask import render_template, make_response

blp = Blueprint("Containers", __name__, url_prefix="/")

@blp.route("/")
class front_page(MethodView):
    def get(self):
        html = render_template("index.html")
        return make_response(html, 200)
    
@blp.route("/admin")
class admin_panel(MethodView):
    def get(self):
        # Get the password and username from the backend, return the rendered page only if it matches
        pass