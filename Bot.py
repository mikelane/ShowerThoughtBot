#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import socket, ssl, yaml, time, re

class Bot:
    def __init__(self, file):
        with open(file, 'r') as y:
            # Load the configs
            config = yaml.load(y)

            # Store the configs in the Bot
            self.server    = config['server']
            self.port      = int(config['port'])
            self.nick      = config['nick']
            self.real_name = config['real_name']
            self.channels  = config['channels']

            # Connect to the server
            self.s = socket.socket()
            self.s.connect((self.server, self.port))
            self.ircsock = ssl.wrap_socket(self.s)
            self.ircsock.send("USER {} 0 * :{}\r\n".format(self.nick,
                                                           self.real_name).encode())
            self.ircsock.send("NICK {}\r\n".format(self.nick).encode())

            # Have to sleep for a couple of potatoes so you don't try to join too early
            time.sleep(2)

            # Join all the channels specified in the config file
            for channel in self.channels:
                self.joinchan(channel['name'], channel['key'])

    def joinchan(self, chan, key):
        self.ircsock.send("JOIN {} {}\r\n".format(chan, key).encode())

    def ping(self):
        self.ircsock.send("PONG :pingis\r\n".encode())

    def sendmsg(self, chan, msg):
        self.ircsock.send("PRIVMSG {} :{}\r\n".format(chan, msg).encode())

    def hello(self, channel, nick):
        self.ircsock.send("PRIVMSG {} :Hello, {}!\r\n".format(channel, nick).encode())

# Initialize a bot!
# bot = Bot('config.yml')
#
# Read, Evaluate, Print, Loop
# while True:
    # Gather some input
    # msg = bot.ircsock.recv(2048).decode()
    # Strip newlines
    # msg = msg.strip('\n\r')
    # Determine what channel the input is from
    # chan = re.search('(\#\w+ )', msg)
    # if chan:
    #     chan = chan.group(1)
        # print("chan: {}".format(chan))
    # Determine what user sent the message
    # fromNick = re.search('(\:\w+\!)', msg)
    # if fromNick:
    #     fromNick = fromNick.group(1)
    #     fromNick = fromNick.strip(':!')
        # print("fromNick: {}".format(fromNick))
    # If the message isn't empty, log it to the screen
    # @todo make this log to a file, too. Write a log function that does both
    # if(msg != ""):
    #     print(msg)

    # If we get a ping, log the ping and execute the ping function
    # if msg.find("PING :") != -1:
    #     print(msg)
    #     bot.ping()

    # When "hello <bot.nick>" is found, call the hello function using
    # the channel that it came from and the user who sent it.
    # if msg.find(":hello {}".format(bot.nick)) != -1:
        # bot.hello(chan, fromNick)