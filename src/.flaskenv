# Variaveis de ambiente para a aplicacao Auspex:

FLASK_APP=${VIRTUAL_ENV}/../dev/src/api_main/api_main_app.py
FLASK_DEBUG=1
FLASK_ENV=development
FLASK_RUN_PORT=8000
FLASK_RUN_HOST=0.0.0.0

# Variaveis de conexao ao banco de dados:

DB_HOST=localhost
DB_PORT=27017
DB_DATABASE=complain_db

# === Variáveis de ativacao do log


API_LOG_FILE=${VIRTUAL_ENV}/../dev/log/api-log.log
API_LOG_ACTIVE=1

# === Variáveis de ativacao da geolocalizacao
USE_GEOLOC=1
