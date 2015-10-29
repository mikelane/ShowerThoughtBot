#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import praw, os.path
from dbadapter import DBAdapter

class Reddit:
    """The Reddit object will handle seeding the database with shower thoughts
    if required and it will update the database with top shower thoughts from
    the last day when asked.
    """
    def __init__(self, dbfile):
        self.user_agent = 'A shower thought grabber'
        self.reddit = praw.Reddit(self.user_agent)
        if not os.path.isfile(dbfile):
            self.seedDB(dbfile)

    def seedDB(self, file):
        submission_list = []
        db = DBAdapter(file)
        submissions = self.reddit.get_subreddit('showerthoughts').get_top_from_all()
        for submission in submissions:
            text = submission.title
            author = '/u/' + submission.author.name
            date = submission.created_utc
            link = submission.short_link
            id = submission.id
            submission_list.append((None, text, author, date, link, id, 0))
        db.insertThoughts(submission_list)


if __name__ == '__main__':
    r = Reddit('test.db')
    print("Finished")
