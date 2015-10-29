#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The base BOT object. This allows you to easily build your own IRC bot by
simply extending the class. For example:

from bot import Bot
class ShowerThoughtBot(Bot):
    def __init__(self, file):
        super().__init__(file)

    Set up your bot's configuration using a yaml file and pass the file to the
    Bot constructor. This class will handle all the connection details and
    will also handle basic functions like sending messages. Your extension
    should have an REPL loop (though I may change that by putting a run
    method in the Bot class).
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import socket, ssl, yaml, time

class Bot:
    def __init__(self, file):
        # @todo add atexit function to close socket on interrupt or error
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

