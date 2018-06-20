from flask import Flask
from flask_restful import Api
from api_util.config import Config
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
api_db = PyMongo(app)

from api_main import api_routes
