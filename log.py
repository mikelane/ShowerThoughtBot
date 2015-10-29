#!/usr/bin/env python3

"""
A basic logger
"""

__author__ = "Mike Lane"
__copyright__ = "Copyright 2015, Michael Lane"
__license__ = "GPL"
__version__ = "3.0"
__email__ = "mikelane@gmail.com"

from datetime import datetime


class Log:
    def log(self, message, severity='info'):
        date = datetime.now()
        date = date.strftime('%Y-%W')
        if severity.lower == 'error':
            logfile = "ERROR-{}.log".format(date)
        elif severity.lower == 'warning':
            logfile = "WARNING-{}.log".format(date)
        else:
            logfile = "INFO-{}.log".format(date)
        with open(logfile, 'a') as log:
            log.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S :: {"
                                              "}".format(message)))
