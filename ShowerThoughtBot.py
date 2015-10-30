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
from datetime import datetime
from dbadapter import DBAdapter

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

    def parseMessage(self, msg, chan, fromNick):
        if msg.find("PING :") != -1:
            self.ping()
        elif (msg.find(":hello {}".format(self.nick)) != -1 or
              msg.find(":hello, {}".format(self.nick)) != -1 or
              msg.find(":hi {}".format(self.nick)) != -1):
            self.log.log(msg, "info")
            self.hello(chan, fromNick)
        elif msg.find(":!showerthought") != -1:
            self.log.log(msg, "info")
            self.printShowerThought(chan, fromNick)
        elif (msg.find(":{}: help".format(self.nick)) != -1 or
              msg.find(":!help") != -1):
            self.log.log(msg, "info")
            self.printHelp(chan)
        elif msg.find(":!source") != -1:
            self.log.log(msg, "info")
            self.printSourceLink(chan)
        else:
            self.log.log(msg, "screen")

    def printSourceLink(self, chan):
        self.ircsock.send("PRIVMSG {} :ShowerThoughtBot is by Mike Lane, https://github.com/mikelane/ShowerThoughtBot\r\n".format(chan).encode())

    def printHelp(self, chan):
        self.ircsock.send("PRIVMSG {} :Get a shower thought with !showerthought\r\n".format(chan).encode())

    def printShowerThought(self, chan, nick):
        db = DBAdapter(self.dbfile)
        thought = db.getRandomThought()
        self.ircsock.send("PRIVMSG {} :okay {}: \"{}\" -{}\r\n".format(
            chan, nick, thought[1], thought[2]).encode())

    def updateDB(self):
        now = datetime.now()
        duration = now - self.update_time
        duration = int(duration.total_seconds())
        if duration >= 86400:
            self.log.log('updating database', 'info')
            self.update_time = now
            self.reddit.getDailyTop()

    # Run the bot!
    def run(self):
        while True:
            fromNick = ""
            self.updateDB()
            # Gather some input
            msg = self.ircsock.recv(2048).decode()
            # Strip newlines
            msg = msg.strip('\n\r')
            # Determine what channel the input is from
            chan = re.search('(\#\w+ )', msg)
            if chan:
                chan = chan.group(1)
                # Determine what user sent the message
                fromNick = re.search('(\:\w+\!)', msg)
                if fromNick:
                    fromNick = fromNick.group(1)
                    fromNick = fromNick.strip(':!')
                    # If the message isn't empty, log it to the screen
            self.parseMessage(msg, chan, fromNick)

# Initialize a bot!
bot = ShowerThoughtBot('config.yml')
bot.run()
