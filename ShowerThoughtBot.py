#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/)'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import socket, ssl, yaml, time, re
from Bot import Bot

class ShowerThoughtBot(Bot):
    def __init__(self, file):
        super().__init__(file)

# Initialize a bot!
bot = ShowerThoughtBot('config.yml')

# Read, Evaluate, Print, Loop
while True:
    # Gather some input
    msg = bot.ircsock.recv(2048).decode()
    # Strip newlines
    msg = msg.strip('\n\r')
    # Determine what channel the input is from
    chan = re.search('(\#\w+ )', msg)
    if chan:
        chan = chan.group(1)
        # print("chan: {}".format(chan))
    # Determine what user sent the message
    fromNick = re.search('(\:\w+\!)', msg)
    if fromNick:
        fromNick = fromNick.group(1)
        fromNick = fromNick.strip(':!')
        # print("fromNick: {}".format(fromNick))
    # If the message isn't empty, log it to the screen
    # @todo make this log to a file, too. Write a log function that does both
    if(msg != ""):
        print(msg)

    # If we get a ping, log the ping and execute the ping function
    if msg.find("PING :") != -1:
        print(msg)
        bot.ping()

    # When "hello <bot.nick>" is found, call the hello function using
    # the channel that it came from and the user who sent it.
    if msg.find(":hello {}".format(bot.nick)) != -1:
        bot.hello(chan, fromNick)
