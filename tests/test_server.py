__author__ = 'Wade Pentz'

import unittest
import sys
sys.path.append('..')
from server import Server, ClientHandler

"""test_server.py

Unit tests for the Server and ClientHandler classes.

To run these tests simply run this script using Python 2.7 in the command line.
    ex: python test_server.py
"""

class ServerUnitTests(unittest.TestCase):
    """Contains all unit tests for Server and ClientHandler classes."""

    @classmethod
    def setUpClass(cls):
        """Instantiate a server object for testing."""
        pass

    def test_pass(self):
        self.assertTrue(True, 'Great job!')

if __name__ == '__main__':
    unittest.main()