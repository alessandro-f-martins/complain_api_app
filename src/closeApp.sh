#!/bin/sh

. ./app_vars.cfg
GUN_PID=$(ps -e | grep gunicorn  | sed "s/\([0-9][0-9]*\).*/\1/g" | head -1)
kill -15 $GUN_PID # SIGTERM
nginx -c $APP_DIR/http/nginx.conf -s quit
mongod --config $APP_DIR/db/init/mongod.conf --shutdown
