from flask import Flask
from flask_smorest import Api

from src.app.blueprints import *
from src.app.lib import limiter

app = Flask(__name__)

app.config["API_TITLE"] = "My Awesome API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"

api = Api(app)

app.config['SECRET_KEY'] = 'super-secret-key'

limiter.init_app(app)

# register the different blueprints
api.register_blueprint(site_blp)
api.register_blueprint(frontend_api_blp)
api.register_blueprint(admin_api_blp)

@app.errorhandler(422)
def handle_unprocessable_entity(err):
    if (hasattr(err, "data")):
        print(err.data)  # inspect in logs
        return {
            "errors": err.data.get("messages", {})
        }, 404
    else:
        print(err)
        return ""

@app.errorhandler(404)
def handle_unprocessable_entity(err):
    if (hasattr(err, "data")):
        print(err.data)  # inspect in logs
        return {
            "errors": err.data.get("messages", {})
        }, 404
    else:
        print(err)
        return ""

@app.errorhandler(405)
def handle_unprocessable_entity(err):
    if (hasattr(err, "data")):
        print(err.data)  # inspect in logs
        return {
            "errors": err.data.get("messages", {})
        }, 405
    else:
        print(err)
        return ""