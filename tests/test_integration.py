__author__ = 'Wade Pentz'

import unittest
import sys
sys.path.append('..')
from server import Server, ClientHandler
from client import Client

"""test_integration.py

Test the integration of the Server and Client models.

To run these tests simply run this script using Python 2.7 in the command line.
    ex: python test_integration.py
"""

class IntegrationTests(unittest.TestCase):
    """Contains all unit tests for Server and ClientHandler classes."""

    @classmethod
    def setUpClass(cls):
        """Instantiate a connect a server and a client."""
        pass

    def test_pass(self):
        self.assertTrue(True, 'Great job!')

if __name__ == '__main__':
    unittest.main()