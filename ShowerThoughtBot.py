#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
My extension of the Bot object. This sets up a database with shower thoughts
and handles the functions that are more specialized to the Shower Thought Bot.
"""
from datetime import datetime
import time

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
        self.update_time = datetime.now()

        # Load the configurations.
        with open(file, 'r') as y:
            # Load the configs
            config = yaml.load(y)

        # Grab the database filename from the configs.
        self.dbfile = config['database']
        # Create a Reddit object to handle the Reddit-specific tasks.
        self.reddit = Reddit(self.dbfile)

    def printShowerThought(self, chan, nick):
        self.ircsock.send("PRIVMSG {} :I'm not quite ready yet, {}\r\n".format(
            channel, nick).encode())

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

            if msg.find(":!showerthought") != -1:
                self.printShowerThought(chan, fromNick)

            # Check the clock
            # now = datetime.now()
            # if now - self.update_time > 86400:
            #     self.update_time = now
            #     self.reddit.getDailyTop()


# Initialize a bot!
bot = ShowerThoughtBot('config.yml')
bot.run()
