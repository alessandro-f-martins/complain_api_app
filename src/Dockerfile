FROM python:3.6.5-alpine3.7

ARG APP_DIR_ARG=/usr/src/app

ENV APP_DIR=$APP_DIR_ARG
ENV LOG_DIR=$APP_DIR_ARG/log

# Variaveis de ambiente para a aplicacao Complain-API:

ENV FLASK_APP=$APP_DIR_ARG/api_main/api_main_app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_PORT=8000
ENV FLASK_RUN_HOST=0.0.0.0

# Variaveis de conexao ao banco de dados:

ENV DB_HOST=localhost
ENV DB_PORT=27017
ENV DB_DATABASE=complain_db

# === Variáveis de ativacao do log

ENV API_LOG_FILE=$LOG_DIR/api-log.log
ENV API_LOG_ACTIVE=1

# === Variáveis de ativacao da geolocalizacao
ENV USE_GEOLOC=1

WORKDIR $APP_DIR_ARG

COPY . .

EXPOSE 80

RUN pip install --no-cache-dir -r requirements.txt \
    && apk add --update mongodb nginx nano \
    && mkdir log db/data db/log

CMD [ "/usr/src/app/runApp.sh" ]
