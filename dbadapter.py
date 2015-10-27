#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import os, sqlite3


conn = sqlite3.connect('example3.db')

c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS thoughts
             (id INTEGER PRIMARY KEY, thought TEXT NOT NULL UNIQUE, author TEXT, date REAL NOT NULL, link TEXT, Reddit_ID TEXT, score INTEGER)''')

try:
    c.execute("INSERT INTO thoughts VALUES (NULL, 'It''s weird to think people who are six foot are only 6 subways tall', '/u/HypnoticHD', 1445804764.0, 'http://redd.it/3q6u9u', '3q6u9u', 0)")
except sqlite3.IntegrityError:
    print("Whoa. Someone already thought that exact same thought!")
conn.commit()
conn.close()