#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
My extension of the Bot object. This sets up a database with shower thoughts
and handles the functions that are more specialized to the Shower Thought Bot.
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/)'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import re, yaml
from bot import Bot
from reddit import Reddit

class ShowerThoughtBot(Bot):
    def __init__(self, file):
        # Initialize the Bot
        super().__init__(file)

        # Load the configurations.
        with open(file, 'r') as y:
            # Load the configs
            config = yaml.load(y)

        # Grab the database filename from the configs.
        self.dbfile = config['database']
        # Create a Reddit object to handle the Reddit-specific tasks.
        self.reddit = Reddit(self.dbfile)

    # Run the bot!
    def run(self):
        while True:
            # Gather some input
            msg = self.ircsock.recv(2048).decode()
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
                self.ping()

            # When "hello <self.nick>" is found, call the hello function using
            # the channel that it came from and the user who sent it.
            if msg.find(":hello {}".format(self.nick)) != -1:
                self.hello(chan, fromNick)

# Initialize a bot!
bot = ShowerThoughtBot('config.yml')
bot.run()
