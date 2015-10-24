#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/)'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import socket, ssl, yaml

class ShowerThoughtBot:
    def __init__(self):
        with open('config.yml', 'r') as y:
            self.c = yaml.load(y)
            self.s = socket.socket()
            self.s.connect((self.c['server'], self.c['port']))
            self.ircsock = ssl.wrap_socket(self.s)
            self.ircsock.send("USER {} {} {} :{}".format(self.c['nick'],
                                                         self.c['nick'],
                                                         self.c['nick'],
                                                         "If everyone on Earth died simultaneously, the Internet would be comprised entirely of bots posting, liking and upvoting each other.").encode())
            self.ircsock.send("NICK {}\n".format(self.c['nick']).encode())
            self.joinchan(self.c['channel'])

    def joinchan(self, chan):
        self.ircsock.send("JOIN {} {}\n".format(chan, self.c['key']).encode())

    def ping(self):
        self.ircsock.send("PONG :pingis\n")

    def sendmsg(self, chan, msg):
        self.ircsock.send("PRIVMSG {} :{}\n".format(chan, msg).encode())

    def hello(self):
        self.ircsock.send("PRIVMSG {} :Hello!\n".format(self.c.channel).encode())

bot = ShowerThoughtBot()
bot.sendmsg(bot.c['channel'], "TESTING!".encode())
