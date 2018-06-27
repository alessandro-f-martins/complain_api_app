'''
--- Complain API microservice application ---
Author: Alessandro Martins
Module: app_main_app
Description: this module is the entry point for the Flask-based application.
It is called by the Gunicorn module, which runs instances of it as worker
processes.
'''
from api_main import application

if __name__ == "__main__":
    application.run()
