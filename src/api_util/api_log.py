import datetime
from api_util.config import Config


class Log():

    _logfile = ''
    _use_log = False

    def __init__(self, logfile=None):
        self._logfile = logfile
        self._use_log = Config.API_LOG_ACTIVE
        if not logfile:
            self._logfile = Config.API_LOG_FILE

    def log_msg(self, msg):
        if self._use_log:
            with open(self._logfile, mode='a', encoding='utf-8') as f:
                f.write('[{}]: {}\n'.format(datetime.datetime.now(), msg))
