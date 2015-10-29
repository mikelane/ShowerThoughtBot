#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import sqlite3

class DBManager:
    """Manage the opening and closing of the sqlite3 database. Use python3
    contexts (with syntax) to automatically open the database, create the cursor
    and then commit the changes and close the database.
    """
    def __init__(self, file):
        self.file = file
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()
