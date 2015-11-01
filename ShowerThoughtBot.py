#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My extension of the Bot object. This sets up a database with shower thoughts
and handles the functions that are more specialized to the Shower Thought Bot.
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/)'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import re, yaml, logging, ssl, getopt, sys
from bot import Bot
from reddit import Reddit
from datetime import datetime
from dbadapter import DBAdapter

# set up logging to file - see previous section for more details
try:
    opts, args = getopt.getopt(sys.argv[1:], "d")
except getopt.GetoptError:
    print("Usage: arguments are -d or --debug=(on|off)")
    exit(2)

LOG_LEVEL = "INFO"
for opt, arg in opts:
    if opt == '-d':
        LOG_LEVEL = "DEBUG"
logger = logging.getLogger('ShowerThoughtBot')
logger.setLevel(logging.getLevelName(LOG_LEVEL))
# create a file handler to log WARNING and higher
date = datetime.now()
date = date.strftime('%Y-%W')
LOG_FILE = "logs/{DATE}.log".format(DATE=date)
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.WARNING)
# create a console handler to handle all log levels
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create a formatter
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %('
                              'message)s', '%H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)
logger.addHandler(fh)

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


    def parse_message(self, msg, chan, fromNick):
        # logger.debug("parse_message starting with msg " + msg)
        if msg.find("PING :") != -1:
            self.ping()
        elif (msg.find(":hello {}".format(self.nick)) != -1 or
              msg.find(":hello, {}".format(self.nick)) != -1 or
              msg.find(":hi {}".format(self.nick)) != -1):
            logger.info(msg)
            self.hello(chan, fromNick)
        elif (msg.find(":!showerthought") != -1 or
              msg.find(":{}: thought".format(self.nick)) != -1 or
              msg.find(":!stb thought") != -1):
            logger.info(msg)
            self.print_shower_thought(chan, fromNick)
        elif (msg.find(":{}: help".format(self.nick)) != -1 or
              msg.find(":!stb help") != -1):
            logger.info(msg)
            self.print_help(chan)
        elif (msg.find(":!stb source") != -1 or
              msg.find(":{}: source".format(self.nick)) != -1):
            logger.info(msg)
            self.print_source_link(chan)
        elif msg.find(":{}: updatedb".format(self.nick)) != -1:
            if not fromNick == 'mlane':
                self.send_message(chan, "Don't tell me what to do!")
            else:
                self.send_message(chan, "Pulling in some thoughts.")
                self.update_database(False)
        elif msg.find(":{}: shruggie".format(self.nick)) != -1:
            logger.debug("trying to print shruggie")
            self.print_shruggie(chan)
        else:
            logger.info(msg)
            return


    def print_source_link(self, chan):
        self.send_message(chan, "ShowerThoughtBot is by Mike Lane, "
                                "https://github.com/mikelane/ShowerThoughtBot")
        self.send_message(chan, "Feel free to fork or report issues.")


    def print_help(self, chan):
        lines = []
        lines.append("I respond to {}: $command or !stb command".format(
            self.nick))
        lines.append("$command = [help|thought|source]")
        lines.append("Get a shower thought with !showerthought.")
        lines.append("More to come...")
        lines.append("mlane@cat.pdx.edu for bugs.")

        for line in lines:
            self.send_message(chan, line)


    def print_shower_thought(self, chan, nick):
        # #self.db_lock.acquire()
        db = DBAdapter(self.dbfile)
        thought = db.get_random_thought()
        self.send_message(chan, "okay {}: \"{}\" -{}\r\n".format(
            nick, thought[1], thought[2]))


    def print_shruggie(self, chan):
        self.send_message(chan, "\udcc2\udcaf\_("
                          "\udce3\udc83\udc84)_/\udcc2\udcaf")


    def update_database(self, Scheduled=True):
        if Scheduled:
            now = datetime.now()
            duration = now - self.update_time
            duration = int(duration.total_seconds())
            if duration >= 86400:
                logger.info('Updating database on schedule.')
                self.update_time = now
                #self.db_lock.acquire()
                self.reddit.get_daily_top()
                #self.db_lock.release()
        else:
            self.reddit.get_daily_top()


    def message_handler(self, message):
        """The message handler breaks out the channel and nick of the sender
        and passes this on to the parser.
        """
        logger.debug("message_handler started with message " + message)
        chan = re.search('(\#\w+ )', message)
        if chan:
            chan = chan.group(1)
        fromNick = re.search('(\:\w+\!)', message)
        if fromNick:
            fromNick = fromNick.group(1)
            fromNick = fromNick.strip(':!')
        self.parse_message(message, chan, fromNick)
        return


    # Run the bot!
    def run(self):
        messages = []
        while True:
            buffer = self.read()
            if len(buffer) > 0:
                messages = buffer.splitlines()
                buffer = ""
            while len(messages) > 0:
                self.message_handler(messages.pop(0))
            self.update_database()


# Initialize a bot!
bot = ShowerThoughtBot('config.yml')
bot.run()
