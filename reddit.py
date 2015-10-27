#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import praw
nsfw_list = {'fuck', 'sex', 'ass', 'cunt', 'whore', 'shit'}
# r = praw.Reddit('OAuth testing example by u/lanemik ver 0.1 '
#                 'see http://github.com/mikelane for source')
# r.set_oauth_app_info(client_id='x33k8j_qKIOEww',
#                      client_secret='p38Mv5GbCikxULc_66sCr4a2wng',
#                      redirect_uri='http://127.0.0.1:65010/authorize_callback')
r = praw.Reddit(user_agent='my cool showerthought grabber')
submissions = r.get_subreddit('showerthoughts').get_top_from_hour(limit=10)
for submission in submissions:
    text = submission.title
    nsfw = any(string in text for string in nsfw_list)
    if not nsfw:
        author = '/u/' + submission.author.name
        date = submission.created_utc
        id = submission.id
        link = submission.short_link
        print("\"{text}\" -{by}, {when} link:{url} id:{id}".format(text = text,
                                                               by   = author,
                                                               when = date,
                                                               url  = link,
                                                               id   = id))
    else:
        print("Hey! None of that language here!")