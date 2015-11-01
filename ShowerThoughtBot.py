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
                    format='[%(levelname)s] %(message)s',
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
        elif (msg.find(":!showerthought") != -1 or
              msg.find(":{}: thought".format(self.nick)) != -1 or
              msg.find(":!stb thought") != -1):
            logging.debug(msg)
            self.printShowerThought(chan, fromNick)
        elif (msg.find(":{}: help".format(self.nick)) != -1 or
              msg.find(":!stb help") != -1):
            logging.debug(msg)
            self.printHelp(chan)
        elif (msg.find(":!stb source") != -1 or
              msg.find(":{}: source".format(self.nick)) != -1):
            logging.debug(msg)
            self.printSourceLink(chan)
        elif msg.find(":{}: updatedb".format(self.nick)) != -1:
            if not fromNick == 'mlane':
                self.ircsock.send("PRIVMSG {} :Don't tell me what to "
                                  "do!\r\n".format(chan).encode('utf-8',
                                                             'surrogateescape'))
            else:
                self.ircsock.send("PRIVMSG {} :Pulling in some "
                                  "thoughts.\r\n".format(chan).encode(
                    'utf-8', 'surrogateescape'))
                self.updateDB(False)
                self.ircsock.send("PRIVMSG {} :Pulled in 5 more shower "
                                  "thoughts\r\n".format(chan).encode('utf-8',
                                  'surrogateescape'))
        elif msg.find(":{}: shruggie".format(self.nick)) != -1:
            logging.debug("trying to print shruggie")
            self.printShruggie(chan)
        else:
            return


    def printSourceLink(self, chan):
        self.ircsock.send("PRIVMSG {} :ShowerThoughtBot is by Mike Lane, "
                          "https://github.com/mikelane/ShowerThoughtBot\r\n"
                          .format(chan).encode('utf-8', 'surrogateescape'))


    def printHelp(self, chan):
        self.ircsock.send("PRIVMSG {} :I respond to showerthoughtbot: "
                          "<command>, !stb <command>, hello "
                          "showerthoughtbot, and hi "
                          "showerthoughtbot\r\n".format(chan).encode(
            'utf-8', 'surrogateescape'))
        self.ircsock.send("PRIVMSG {} :Current commands are \"thought\", "
                          "\"help\", and \"source\"\r\n".format(
            chan).encode('utf-8', 'surrogateescape'))
        self.ircsock.send("PRIVMSG {} :Or get a shower thought with "
                          "!showerthought\r\n".format(chan).encode('utf-8',
                                                             'surrogateescape'))
        self.ircsock.send("PRIVMSG {} :More to come.\r\n".format(
            chan).encode('utf-8', 'surrogateescape'))


    def printShowerThought(self, chan, nick):
        # #self.db_lock.acquire()
        db = DBAdapter(self.dbfile)
        thought = db.getRandomThought()
        # #self.db_lock.release()
        self.ircsock.send("PRIVMSG {} :okay {}: \"{}\" -{}\r\n".format(
            chan, nick, thought[1], thought[2]).encode('utf-8',
                                                        'surrogateescape'))


    def printShruggie(self, chan):
        self.ircsock.send("PRIVMSG {} : \udcc2\udcaf\_("
                          "\udce3\udc83\udc84)_/\udcc2\udcaf\r\n".format(
            chan).encode('utf-8', 'surrogateescape'))


    def updateDB(self, Scheduled=True):
        if Scheduled:
            now = datetime.now()
            duration = now - self.update_time
            duration = int(duration.total_seconds())
            if duration >= 86400:
                logging.debug('Updating database on schedule.')
                self.update_time = now
                #self.db_lock.acquire()
                self.reddit.getDailyTop()
                #self.db_lock.release()
        else:
            self.reddit.getDailyTop()

            
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


    def read(self, buffsize=4096):
        buffer = ""
        while True:
            try:
                buffer += self.ircsock.recv(buffsize).decode('utf-8',
                                                             'surrogateescape')
            except ssl.SSLWantReadError:
                return buffer


    # Run the bot!
    def run(self):
        messages = []
        while True:
            buffer = self.read()
            if len(buffer) > 0:
                messages = buffer.splitlines()
                buffer = ""
            while len(messages) > 0:
                self.messageHandler(messages.pop(0))
            self.updateDB()


# Initialize a bot!
bot = ShowerThoughtBot('config.yml')
bot.run()
