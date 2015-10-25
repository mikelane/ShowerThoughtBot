#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/)'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import socket, ssl, yaml, time

class ShowerThoughtBot:
    def __init__(self):
        with open('config.yml', 'r') as y:
            self.c = yaml.load(y)
            self.s = socket.socket()
            self.s.connect((self.c['server'], self.c['port']))
            self.ircsock = ssl.wrap_socket(self.s)
            time.sleep(2)
            self.ircsock.send("USER {} {} {} :{}\r\n".format(self.c['nick'],
                                                             self.c['nick'],
                                                             self.c['nick'],
                                                             self.c['nick']).encode())
            self.ircsock.send("NICK {}\r\n".format(self.c['nick']).encode())

    def joinchan(self, chan):
        self.ircsock.send("JOIN {} {}\r\n".format(chan, self.c['key']).encode())

    def ping(self):
        self.ircsock.send("PONG :pingis\r\n".encode())

    def sendmsg(self, chan, msg):
        self.ircsock.send("PRIVMSG {} :{}\r\n".format(chan, msg).encode())

    def hello(self):
        self.ircsock.send("PRIVMSG {} :Hello!\r\n".format(self.c['channel']).encode())

bot = ShowerThoughtBot()
time.sleep(2)
bot.joinchan(bot.c['channel'])

while 1:
    msg = bot.ircsock.recv(2048).decode()
    msg = msg.strip('\n\r')
    if(msg != ""):
        print(msg)

    if msg.find("PING :") != -1:
        print(msg)
        bot.ping()

    if msg.find(":hello {}".format(bot.c['nick'])) != -1:
        bot.hello()
