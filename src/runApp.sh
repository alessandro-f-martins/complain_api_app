#!/bin/sh

# . ./app_vars.cfg
# . ../../venv/bin/activate
mongod --config $APP_DIR/db/init/mongod.conf &
nginx -c $APP_DIR/http/nginx.conf
gunicorn --workers 3 --bind 0.0.0.0:5000 api_main.api_main_app
