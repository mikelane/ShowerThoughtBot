#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An adapter for the SQLite3 database so that the ShowerThoughtBot class can
make pythonic calls rather than database calls.
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import logging, re
from dbmanager import DBManager
from sqlite3 import IntegrityError

logger = logging.getLogger('ShowerThoughtBot')

class DBAdapter:
    def __init__(self, file):
        self.file = file
        self.create_database()
        self.vulgarities = set()
        with open('rotated_vulgarities.txt', 'r') as f:
            for line in f:
                self.vulgarities.add(self.rot13(line.rstrip()))

    def rot13(self, word):
        rot13_data = bytes.maketrans(b"ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",b"NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
        return word.translate(rot13_data)

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
            while True:
                c.execute('SELECT * FROM thoughts ORDER BY RANDOM() LIMIT 1')
                result = c.fetchone()
                result_words = re.split('[\W]+', result)
                result_words = set([word.lower() for word in result_words])
                if self.vulgarities.isdisjoint(result_words):
                    return result
                else:
                    logger.warning("Filtered a vulgar showerthought.")

