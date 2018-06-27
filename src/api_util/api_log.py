'''
--- Complain API microservice application ---
Author: Alessandro Martins
Module: api_log
Description: log file processing module
'''
import datetime
from api_util.config import Config


class Log():
    '''
    Log file processing class
    '''
    _logfile = ''
    _use_log = False

    def __init__(self, logfile=None):
        '''
        __init__
        '''
        self._logfile = logfile
        # Defines if logging is on
        self._use_log = Config.API_LOG_ACTIVE
        if not logfile:
            self._logfile = Config.API_LOG_FILE

    def log_msg(self, msg):
        '''
        Writes messages to log file
        '''
        if self._use_log:
            with open(self._logfile, mode='a', encoding='utf-8') as f:
                f.write('[{}]: {}\n'.format(datetime.datetime.now(), msg))
