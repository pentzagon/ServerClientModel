__author__ = 'Wade Pentz'

import asyncore
import asynchat
import socket
import os
import time
import logging
import unittest
from config import Config
from logs import server_log

"""Server.py

Server class that logs performance data from multiple test clients.

More details

Example of usage:
Stuff

"""

class Server(asyncore.dispatcher):
    """Server class that logs performance data from multiple, concurrent test clients.

    More details here.

    Args:
        param1 (int): first parameter.

    Attributes:
        att1 (int): does stuff.
    """

    def __init__(self, port=Config["port"]):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, 80))
        self.buffer = 'GET %s HTTP/1.0\r\n\r\n' % path
        self.init_log()

    def init_log(self):
        """Initializes the client data log."""
        pass

    def handle_accept(self):
        """Handles a client connection by creating a ConnectedClient instance for it."""
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            server_log.debug('Incoming connection from {}'.format(addr))
            handler = EchoHandler(sock)


class ConnectedClient(): # TODO - Call this ClientHandler()??
    """Class instantiated to keep track of each client that connects to the server.

    More details here.
    """

    def __init__(self):
        pass

class ServerUnitTests(unittest.TestCase):
    """Contains all unit tests for Server and ConnectedClient classes."""

    def test_pass(self):
        self.assertTrue(True, 'Great job!')

if __name__ == '__main__':
    server = Server()
    try:
        server.run()
    except KeyboardInterrupt:
        print "Ended via keyboard interrupt"
    except Exception as e:
        print server_log.debug('Faulted during execution.')
        raise e
    finally:
        server.end()