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

import socket, ssl, yaml, time, threading, logging, atexit

logger = logging.getLogger('ShowerThoughtBot')

class Bot:
    def __init__(self, file):
        with open(file, 'r') as y:
            # Load the configs
            config = yaml.load(y)

        self.socket_lock = threading.Lock()
        #self.db_lock = threading.Lock()

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
        self.ircsock.setblocking(0)
        self.socket_lock.acquire()
        self.ircsock.send("USER {} 0 * :{}\r\n".format(self.nick,
                                                       self.real_name)
                           .encode('utf-8', 'surrogateescape'))
        self.ircsock.send("NICK {}\r\n".format(self.nick).encode('utf-8',
                                                             'surrogateescape'))
        self.socket_lock.release()
        # Have to sleep for a couple of potatoes so you don't try to join too early
        # @todo do a callback lambda instead?
        time.sleep(2)

        # Join all the channels specified in the config file
        for channel in self.channels:
            self.join_channel(channel['name'], channel['key'])

        # Register a function to close the socket upon exit or interrupt
        atexit.register(closeSocket, self.ircsock)


    def read(self, buffsize=4096):
        buffer = ""
        while True:
            try:
                buffer += self.ircsock.recv(buffsize).decode('utf-8',
                                                             'surrogateescape')
            except ssl.SSLWantReadError:
                return buffer


    def join_channel(self, chan, key):
        self.ircsock.send("JOIN {} {}\r\n".format(chan, key).encode('utf-8',
                                                             'surrogateescape'))

    def ping(self):
        logger.debug("Sending PONG")
        self.ircsock.send("PONG :pingis\r\n".encode('utf-8', 'surrogateescape'))

    def send_message(self, chan, msg):
        self.ircsock.send("PRIVMSG {} :{}\r\n".format(chan, msg).encode(
             'utf-8', 'surrogateescape'))

    def hello(self, channel, nick):
        self.ircsock.send("PRIVMSG {} :Hello, {}!\r\n".format(channel, nick)
                          .encode('utf-8', 'surrogateescape'))

def closeSocket(socket):
    logger.warning('Closing socket')
    socket.close()

