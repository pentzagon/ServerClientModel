__author__ = 'Wade Pentz'

import unittest
import sys
sys.path.append('..')
from client import Client

"""test_client.py

Unit tests for the Client class.

To run these tests simply run this script using Python 2.7 in the command line.
    ex: python test_client.py
"""

class ClientUnitTests(unittest.TestCase):
    """Contains all unit tests for Client class."""

    @classmethod
    def setUpClass(cls):
        """Instantiate a server object for testing."""
        pass

    def test_pass(self):
        self.assertTrue(True, 'Great job!')

if __name__ == '__main__':
    unittest.main()