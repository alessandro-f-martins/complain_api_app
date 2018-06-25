'''
    config.py: arquivo de configuracao do sistema API ReclameAqui
'''
import os
from dotenv import load_dotenv

# === Obtendo as variaveis de ambiente e carregando com o dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=BASEDIR + '../.flaskenv')


class Config(object):
    ''' Config: classe global de configuracao
    '''
    # === Variáveis de configuracao do MongoDB

    # MONGO_USERNAME = os.getenv('DB_USER')
    # MONGO_PASSWORD = os.getenv('DB_PASSWD')
    MONGO_HOST = os.getenv('DB_HOST')
    MONGO_PORT = os.getenv('DB_PORT')
    MONGO_DBNAME = os.getenv('DB_DATABASE')
    MONGO_URI = "mongodb://%s:%s/%s" % (MONGO_HOST, MONGO_PORT, MONGO_DBNAME)

    # === Variáveis de ativacao do log

    API_LOG_ACTIVE = (os.getenv('API_LOG_ACTIVE', '0') == '1')
    API_LOG_FILE = os.getenv('API_LOG_FILE')

    USE_GEOLOC = (os.getenv('USE_GEOLOC', '0') == '1')
    GKEY = 'AIzaSyDRnUVxmIT4uvWEUs_WNBeQBwnZZP5TV6U'
