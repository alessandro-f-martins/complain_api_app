from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo
from api_util.config import Config


application = Flask(__name__)
application.config.from_object(Config)
api = Api(application)
api_db = PyMongo(application)

from api_main import api_routes
