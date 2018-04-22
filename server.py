__author__ = 'Wade Pentz'

import os
import time
import logging
import asyncore
import asynchat
import socket
from config import Config
from logs import server_log, file_formatter

"""server.py

Stuff.

More details

Example of usage:
Stuff

"""

class Server(asyncore.dispatcher):
    """Server class that logs performance data from multiple, concurrent test clients.

    Sets up an asynchronous server that records test results sent by connected clients. 
    A ClientHandler object is created for each new client that connects. Clients communicate 
    with the server using a string messaging protocol.

    Args:
        host (str): address where test server will run.
        port (int): network port the server will run on.
    """

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.client_id = Config["first_client_id"]
        self.num_connected_clients = 0
        self.init_log()
        self.init_server_socket()
        self.start_time = time.strftime('%Y-%m-%d_%H:%M:%S')
        self.end_time = None

    def init_log(self):
        """Initializes the server's log file for client data."""
        try:
            os.makedirs(Config["server_log_path"])
        except OSError:
            if not os.path.isdir(Config["server_log_path"]):
                raise
        server_log_file = logging.FileHandler(Config["server_log_path"] + 'server_log_' + 
                                                time.strftime('%Y-%m-%d_%H.%M.%S') + '.txt')
        server_log_file.setLevel(logging.DEBUG)
        server_log_file.setFormatter(file_formatter)
        server_log.addHandler(server_log_file)

    def init_server_socket(self):
        """Create, bind, and configure socket for server."""
        server_log.info('Initializing server on {}:{}'.format(self.host, self.port))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.host, self.port))
        self.listen(5)
        server_log.info('Initialization complete!')

    def handle_accept(self):
        """Handles a client connection and creates a ClientHandler instance for it."""
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            server_log.info('Incoming connection from {},' \
                'assigning client id {}'.format(repr(addr), self.client_id))
            ClientHandler(sock, addr, self.client_id)
            self.client_id += 1
            self.num_connected_clients += 1

    def execute(self):
        """Execute asyncore.loop until all clients are closed"""
        server_log.info('Server now accepting test client connections.')
        while not self.clients_done():
            asyncore.loop(timeout=1, count=1)

    def clients_done(self):
        """Returns True if all clients have completed their tests."""
        if self.num_connected_clients == 0:
            return False
        elif len(asyncore.socket_map) > 1:
            return False
        else:
            return True

    def write_report(self):
        """Writes out a report of the test clients that ran on the server"""
        self.end_time = time.strftime('%Y-%m-%d_%H:%M:%S')
        server_log.info()
    
class ClientHandler(asynchat.async_chat):
    """Class instantiated to keep track of each client that connects to the server.

    Args:
        sock (int): address for socket on which the client is connected.
        addr (int): 
        id (int): unique identifier for client.
    """

    def __init__(self, sock, addr, client_id):
        asynchat.async_chat.__init__(self, sock=sock)
        self.addr = addr
        self.client_id = client_id
        self.set_terminator(Config["msg_terminator"])
        self.buffer = [] 

    def collect_incoming_data(self, data):
        """Buffer incoming message"""
        self.buffer.append(data)

    # TODO - REWRITE THIS FUNCTION!
    def found_terminator(self):
        """Process incoming message"""
        self.current_msg = ''.join(self.buffer)

        # TODO - rewrite this part:
        cmd = self.current_msg.split(',')[0]
        try:
            self.cmd_dict[cmd]()
        except KeyError:
            msg = 'Invalid client message received from port:{}'.format(self.addr[1])
            print msg
            self.server_log.info(msg)
        # END REWRITE

        self.buffer = []


if __name__ == '__main__':
    server = None
    try:
        server = Server(Config["host"], Config["port"])
        server.execute()
    except KeyboardInterrupt:
        print "Keyboard interrupt: Shutting server down..."
    #except Exception as e:
    #    print server_log.debug('Exception raised at runtime: {}'.format(repr(e)))
    #    raise e
    finally:
        if server:
            server.write_report()
            server.close()