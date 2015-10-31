#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
My extension of the Bot object. This sets up a database with shower thoughts
and handles the functions that are more specialized to the Shower Thought Bot.
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/)'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import re, yaml, threading
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
        self.socket_lock = threading.Lock()
        self.db_lock = threading.Lock()


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
        self.socket_lock.acquire()
        self.ircsock.send("PRIVMSG {} :ShowerThoughtBot is by Mike Lane, https://github.com/mikelane/ShowerThoughtBot\r\n".format(chan).encode())
        self.socket_lock.release()

    def printHelp(self, chan):
        self.socket_lock.acquire()
        self.ircsock.send("PRIVMSG {} :Get a shower thought with !showerthought\r\n".format(chan).encode())
        self.socket_lock.release()

    def printShowerThought(self, chan, nick):
        self.db_lock.acquire()
        db = DBAdapter(self.dbfile)
        thought = db.getRandomThought()
        self.db_lock.release()
        self.socket_lock.acquire()
        self.ircsock.send("PRIVMSG {} :okay {}: \"{}\" -{}\r\n".format(
            chan, nick, thought[1], thought[2]).encode())
        self.socket_lock.release()

    def updateDB(self):
        now = datetime.now()
        duration = now - self.update_time
        duration = int(duration.total_seconds())
        if duration >= 86400:
            self.log.log('updating database', 'info')
            self.update_time = now
            self.db_lock.acquire()
            self.reddit.getDailyTop()
            self.db_lock.release()

    # Run the bot!
    def run(self):
        threads = []
        while True:
            self.updateDB()
            # Gather some input
            message = ''
            self.socket_lock.acquire()
            c = self.ircsock.recv(1).decode()
            nextC = self.ircsock.recv(1).decode()
            messages = []
            while not nextC == '':
                if c == '\r' and nextC == '\n' and len(message) > 0:
                    messages.append(message)
                    message.clear()
                    c = self.ircsock.recv(1).decode()
                    nextC = self.ircsock.recv(1).decode()
                message += c
                c = nextC
                nextC = self.ircsock.recv(1).decode()
            self.socket_lock.release()

            # @todo, this is where we spawn as many threads as there are messages
            # @todo, and in those threads handle the message and then die.
            # @todo, Note: acquire a lock to utilize socket. Also acquire lock to
            # @todo, utilize the database

            for i in range(len(messages)):
                t = threading.Thread(target=messageHandler, args=(messages[i],))
                threads.append(t)
                t.start()

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
