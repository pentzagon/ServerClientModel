__author__ = 'Wade Pentz'

import unittest
import sys
import logging
import os
import shutil
sys.path.append('..')
from client import Client, FileWriterClient
from config import config
from logs import client_log

"""test_client.py

Unit tests for the Client class.

To run these tests simply run this script using Python 2.7 in the command line.
    ex: python test_client.py
"""

class ClientUnitTests(unittest.TestCase):
    """Contains all unit tests for Client class."""

    @classmethod
    def setUpClass(cls):
        client_log.setLevel(logging.ERROR)
        cls.default_run_time = 1
        cls.default_chunk_size = 10
        cls.default_file_size = 50

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(config["client_log_path"]):
            shutil.rmtree(config["client_log_path"])
        if os.path.isdir(config["client_file_path"]):
            shutil.rmtree(config["client_file_path"])

    def test_good_chunk_size(self):
        try:
            client = FileWriterClient(config["host"], config["port"], run_time=self.default_run_time, 
                    chunk_size=self.default_chunk_size, file_size=self.default_file_size)
        except ValueError:
            self.fail("fail")

    def test_chunk_size_too_small(self):
        for chunk_size in range(1,10):
            with self.assertRaises(ValueError):
                client = FileWriterClient(config["host"], config["port"], run_time=self.default_run_time, 
                    chunk_size=chunk_size, file_size=self.default_file_size)

    def test_chunk_size_larger_than_file(self):
        chunk_size = 6
        with self.assertRaises(ValueError):
            client = FileWriterClient(config["host"], config["port"], run_time=self.default_run_time, 
                chunk_size=chunk_size, file_size=self.default_file_size)

    def test_file_rollover_check(self):
        file_size = 1000
        with self.assertRaises(ValueError):
            client = FileWriterClient(config["host"], config["port"], run_time=self.default_run_time, 
                chunk_size=self.default_chunk_size, file_size=file_size)


if __name__ == '__main__':
    unittest.main()