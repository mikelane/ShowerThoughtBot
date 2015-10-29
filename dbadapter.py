#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

from dbmanager import DBManager
from sqlite3 import IntegrityError

class DBAdapter:
    def __init__(self, file):
        self.file = file
        self.createDB()

    def createDB(self):
        with DBManager(self.file) as c:
            c.execute('''CREATE TABLE IF NOT EXISTS thoughts
                  (id INTEGER PRIMARY KEY,
                  thought TEXT NOT NULL UNIQUE,
                  author TEXT,
                  date REAL NOT NULL,
                  link TEXT,
                  Reddit_ID TEXT,
                  score INTEGER)''')

    def insertThoughts(self, data):
        with DBManager(self.file) as c:
            # c.executemany('INSERT INTO thoughts VALUES (?, ?, ?, ?, ?, ?, ?)', data)
            for item in data:
                try:
                    c.execute('INSERT INTO thoughts VALUES (?, ?, ?, ?, ?, ?, ?)', item)
                except IntegrityError:
                    pass