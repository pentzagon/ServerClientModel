__author__ = 'Wade Pentz'

import unittest
import sys
import logging
import os
import shutil
import socket
sys.path.append('..')
from server import Server, ClientHandler
from config import config
from logs import server_log

"""test_server.py

Unit tests for the Server and ClientHandler classes.

To run these tests simply run this script using Python 2.7 in the command line.
    ex: python test_server.py
"""

class ServerUnitTests(unittest.TestCase):
    """Contains all unit tests for Server and ClientHandler classes."""

    @classmethod
    def setUpClass(cls):
        server_log.setLevel(logging.ERROR)

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(config["server_log_path"]):
            shutil.rmtree(config["server_log_path"])

    def setUp(self):
        self.server = Server(config["host"], config["port"])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_handler = ClientHandler(s, 'test.test', 0)

    def tearDown(self):
        if self.server:
            self.server.close()
            self.server = None
        if self.client_handler:
            self.client_handler.close()
            self.client_handler = None

    def test_clients_not_done(self):
        self.server.client_list = {}
        self.assertFalse(self.server.clients_done())

    def test_clients_done(self):
        self.server.client_list = {"100": "test"}
        self.client_handler.close()
        self.assertTrue(self.server.clients_done())

    def test_bad_file_stats(self):
        self.client_handler.msg_split = ['test']
        self.assertFalse(self.client_handler.handle_file_stats())

    def test_good_file_stats(self):
        self.client_handler.msg_split = ['test', 0, 0]
        self.assertTrue(self.client_handler.handle_file_stats())

    def test_bad_perf_stats(self):
        self.client_handler.msg_split = ['test']
        self.assertFalse(self.client_handler.handle_perf_stats())

    def test_good_perf_stats(self):
        self.client_handler.msg_split = ['test', 0, 0]
        self.assertTrue(self.client_handler.handle_perf_stats())
    

if __name__ == '__main__':
    unittest.main()