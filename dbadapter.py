#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An adapter for the SQLite3 database so that the ShowerThoughtBot class can
make pythonic calls rather than database calls.
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import logging
from dbmanager import DBManager
from sqlite3 import IntegrityError


class DBAdapter:
    def __init__(self, file):
        self.file = file
        self.create_database()


    def create_database(self):
        with DBManager(self.file) as c:
            c.execute('''CREATE TABLE IF NOT EXISTS thoughts
                  (id INTEGER PRIMARY KEY,
                  thought TEXT NOT NULL UNIQUE,
                  author TEXT,
                  date REAL NOT NULL,
                  link TEXT,
                  Reddit_ID TEXT,
                  score INTEGER)''')


    def insert_thoughts(self, data):
        with DBManager(self.file) as c:
            for item in data:
                try:
                    c.execute('INSERT INTO thoughts VALUES (?, ?, ?, ?, ?, ?, ?)', item)
                except IntegrityError:
                    pass


    def get_random_thought(self):
        with DBManager(self.file) as c:
            c.execute('SELECT * FROM thoughts ORDER BY RANDOM() LIMIT 1')
            return c.fetchone()