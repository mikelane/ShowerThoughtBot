#!/usr/bin/env python3

"""
A basic logger
"""

__author__ = "Mike Lane"
__copyright__ = "Copyright 2015, Michael Lane"
__license__ = "GPL"
__version__ = "3.0"
__email__ = "mikelane@gmail.com"

import os, errno
from datetime import datetime

class Log:
    def __init__(self, msg_format='%Y-%m-%d %H:%M:%S'):
        self.msg_format = msg_format
        try:
            os.makedirs('logs/')
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def log(self, message, severity='screen'):
        date = datetime.now()
        # Weekly logs are probably sufficient.
        date = date.strftime('%Y-%W')
        if severity == 'error':
            logfile = "logs/ERROR-{}.log".format(date)
        elif severity == 'warning':
            logfile = "logs/WARNING-{}.log".format(date)
        else:
            logfile = "logs/INFO-{}.log".format(date)

        msg_date = datetime.now().strftime(self.msg_format)
        print("{} :: {}".format(msg_date, message))

        if not severity == 'screen':
            with open(logfile, 'a') as log:
                log.write(
                    datetime.now().strftime("{} :: {}\n".format(msg_date,
                                                              message)))

if __name__ == '__main__':
    l = Log()
    l.log("OMG OMG OMG!", "error")
    l.log("not as bad", "warning")
    l.log("super easy", "info")
    l.log("just to the screen, baby", "screen")
