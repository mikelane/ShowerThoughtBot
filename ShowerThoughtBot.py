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
        # #self.db_lock.acquire()
        db = DBAdapter(self.dbfile)
        thought = db.getRandomThought()
        # #self.db_lock.release()
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
            #self.db_lock.acquire()
            self.reddit.getDailyTop()
            #self.db_lock.release()
            
    def messageHandler(self, message):
        chan = re.search('(\#\w+ )', message)
        if chan:
            chan = chan.group(1)
        fromNick = re.search('(\:\w+\!)', message)
        if fromNick:
            fromNick = fromNick.group(1).strip(':!')
        self.parseMessage(message, chan, fromNick)

    # Run the bot!
    def run(self):
        threads = []
        while True:
            # initialize data structures
            buffer = ''
            messages = []

            # Acquire the socket lock
            self.socket_lock.acquire()

            # prime the pump with first character and lookahead character
            c = self.ircsock.recv(1).decode()
            nextC = self.ircsock.recv(1).decode()

            # gather input one char at a time
            while not (c == '' or nextC == ''):
                # If we've found the end of a message
                if c == '\r' and nextC == '\n' and len(buffer) > 0:
                    # Put the message into the list and clear the buffer
                    messages.append(buffer)
                    buffer.clear()

                    # Gather the next character and the lookahead
                    c = self.ircsock.recv(1).decode()
                    # if there is no next character, go and deal with the messages
                    if c == '':
                        break
                    nextC = self.ircsock.recv(1).decode()

                # If the end of input hasn't been reached, append c to the buffer
                # and move to the next character.
                buffer += c
                c = nextC
                nextC = self.ircsock.recv(1).decode()

            # release the lock
            self.socket_lock.release()

            # Start a thread to handle each of the received messages
            for message in range(len(messages)):
                t = threading.Thread(target=self.messageHandler, args=(message,))
                threads.append(t)
                t.start()

            # Start a thread to update the db if required.
            updatedb = threading.Thread(name='DBUpdater', target=self.updateDB())
            updatedb.start()

# Initialize a bot!
bot = ShowerThoughtBot('config.yml')
bot.run()
