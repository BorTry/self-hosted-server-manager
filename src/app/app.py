from flask import Flask
from flask_smorest import Api

from src.app.blueprints import *

app = Flask(__name__)

app.config["API_TITLE"] = "My Awesome API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"

api = Api(app)

# register the different blueprints
api.register_blueprint(site_blp)
api.register_blueprint(api_blp)