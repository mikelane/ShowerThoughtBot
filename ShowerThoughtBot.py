#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
My extension of the Bot object. This sets up a database with shower thoughts
and handles the functions that are more specialized to the Shower Thought Bot.
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/)'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import re, yaml, threading, logging, ssl
from bot import Bot
from reddit import Reddit
from datetime import datetime
from dbadapter import DBAdapter

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


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
        # logging.debug("parseMessage starting with msg " + msg)
        if msg.find("PING :") != -1:
            self.ping()
        elif (msg.find(":hello {}".format(self.nick)) != -1 or
              msg.find(":hello, {}".format(self.nick)) != -1 or
              msg.find(":hi {}".format(self.nick)) != -1):
            logging.debug(msg)
            self.hello(chan, fromNick)
        elif msg.find(":!showerthought") != -1:
            logging.debug(msg)
            self.printShowerThought(chan, fromNick)
        elif (msg.find(":{}: help".format(self.nick)) != -1 or
              msg.find(":!help") != -1):
            logging.debug(msg)
            self.printHelp(chan)
        elif msg.find(":!source") != -1:
            logging.debug(msg)
            self.printSourceLink(chan)
        else:
        #     logging.debug(msg)

            return

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
            logging.debug('Updating database')
            self.update_time = now
            #self.db_lock.acquire()
            self.reddit.getDailyTop()
            #self.db_lock.release()
            
    def messageHandler(self, message):
        logging.debug("messageHandler started with message " + message)
        chan = re.search('(\#\w+ )', message)
        if chan:
            chan = chan.group(1)
        fromNick = re.search('(\:\w+\!)', message)
        if fromNick:
            fromNick = fromNick.group(1)
            fromNick = fromNick.strip(':!')
        self.parseMessage(message, chan, fromNick)
        # logging.debug("messageHandler ending")
        return

    def getNextChar(self):
        """Must posses socket_lock when executing this function!"""
        try:
            character = self.ircsock.recv(1).decode()
        except ssl.SSLWantReadError:
            character = ''

        return character



    # Run the bot!
    def run(self):
        threads = []
        while True:
            logging.debug("len(threads) = " + str(len(threads)))
            while len(threads) > 0 and threads[0].isAlive:
                threads.pop(0)
            # for thread in threads:
            #     if thread.isAlive():
            #         pass
            #     else:
            #         del thread
            # logging.debug("len(threads) = " + str(len(threads)))
            # logging.debug("begining of REPL loop")
            # initialize data structures
            buffer = ""
            messages = []

            # Acquire the socket lock
            self.socket_lock.acquire()

            # prime the pump with first character and lookahead character
            c0 = self.getNextChar()
            c1 = self.getNextChar()

            # gather input one char at a time
            while c0 != '':
                # logging.debug("Inner REPL")
                # If we've found the end of a message
                if c0 == '\r' and c1 == '\n':
                    # sometimes the first character (':') doesn't make it in. So add it
                    # since all IRC messages start with a ':'.
                    if not buffer.startswith(':'):
                        buffer = ':' + buffer

                    # Put the message into the list and clear the buffer
                    if not (buffer.startswith(":iss.cat.pdx.edu") or
                            buffer.startswith(":showerthoughtbot!")):
                        logging.debug("buffer is " + buffer)
                        messages.append(buffer)
                    buffer = ""

                # If the end of input hasn't been reached, append c to the buffer
                # and move to the next character.
                buffer += c0
                if c1 == '\n':
                    c0 = self.getNextChar()
                else:
                    c0 = c1

                c1 = self.getNextChar()

            # release the lock
            # logging.debug("Releasing socket lock")
            self.socket_lock.release()

            for m in messages:
                # Start a thread to handle each of the received messages
                t = threading.Thread(target=self.messageHandler, args=(m,))
                threads.append(t)
                # logging.debug("Starting messageHandler")
                t.start()

            # Start a thread to update the db if required.
            updatedb = threading.Thread(name='DBUpdater', target=self.updateDB())
            updatedb.start()

# Initialize a bot!
bot = ShowerThoughtBot('config.yml')
bot.run()
