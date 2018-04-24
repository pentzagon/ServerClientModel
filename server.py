__author__ = 'Wade Pentz'

import os
import time
import logging
import asyncore
import asynchat
import socket
from config import config
from client_api import client_api
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
    CONNECTION_MAP = {}

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)# map=Server.CONNECTION_MAP)
        self.host = host
        self.port = port
        self.client_id = config["first_client_id"]
        self.client_list = {}
        self.init_log_file()
        self.init_server_socket()
        self.start_time = time.strftime('%Y-%m-%d_%H:%M:%S')
        self.end_time = None
        self.run_loop()

    def init_log_file(self):
        """Initializes the server's log file for client data."""
        try:
            os.makedirs(config["server_log_path"])
        except OSError:
            if not os.path.isdir(config["server_log_path"]):
                raise
        server_log_file = logging.FileHandler(config["server_log_path"] + 'server_log_' + 
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
        """Handles a client connection - Creates a ClientHandler instance for it.
        The ClientHandler is stored according to client_id in the client_list dictionary."""
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            server_log.info('Client connection from {}, assigning client id {}'.format(repr(addr), self.client_id))
            handler = ClientHandler(sock, addr, self.client_id)
            self.client_list.update({self.client_id: handler})
            # TODO - DELETE THIS PRINT
            server_log.debug('client_list = {}'.format(self.client_list))
            self.client_id += 1

    def handle_close(self):
        server_log.info('Server shutting down...')
        self.close()

    def run_loop(self):
        """Run asyncore.loop until all clients are closed"""
        server_log.info('Server now accepting client connections.')
        while not self.clients_done():
            asyncore.loop(timeout=config["server_timeout"], count=config["server_loop_count"])
                          #map=Server.CONNECTION_MAP, 

    def clients_done(self):
        """Returns True if all clients have completed their tests and at least one client has connected."""
        if len(self.client_list) == 0:
            return False
        #elif len(Server.CONNECTION_MAP) > 1:
        elif len(asyncore.socket_map) > 1:
            return False
        else:
            return True

    def write_report(self):
        """Writes out a report that displays data for all clients that ran."""
        #self.end_time = time.strftime('%Y-%m-%d_%H:%M:%S')
        pass


class ClientHandler(asynchat.async_chat):
    """Class instantiated to keep track of each client that connects to the server.

    Args:
        sock (int): socket on which the client is connected.
        addr (int): address on which the client is connected.
        id (int): unique identifier for client.
    """

    def __init__(self, sock, addr, client_id):
        asynchat.async_chat.__init__(self, sock=sock)#, map=Server.CONNECTION_MAP)
        self.addr = addr
        self.client_id = client_id
        self.set_terminator(client_api["terminator"])
        self.msg_buffer = []
        self.msg = ''
        self.msg_handler = {client_api["get_client_id"]: self.handle_get_client_id,
                            client_api["heartbeat"]: self.handle_heartbeat, 
                            client_api["ready"]: self.handle_ready }
        # TODO - REMOVE THESE PRINTS OR CHANGE LEVEL TO INFO
        server_log.debug("ClientHandler spawned with addr={}, client_id={}".format(addr, client_id))
        #server_log.debug("Server.CONNECTION_MAP = {}".format(repr(Server.CONNECTION_MAP)))

    def collect_incoming_data(self, data):
        """Buffer incoming message"""
        # TODO - delet print
        server_log.info('collect_incoming_data {}'.format(data))
        self.msg_buffer.append(data)

    def found_terminator(self):
        """Processes the incoming message by looking up the handler in the message dictionary."""
        self.msg = ''.join(self.msg_buffer)
        server_log.info('Received message from client id {}: {}'.format(self.client_id, self.msg))
        cmd = self.msg.split(client_api["delimiter"])[0]
        try:
            self.msg_handler[cmd]()
        except KeyError as e:
            server_log.info('Unhandled command received from client id {}: {}'.format(self.client_id, cmd))
        # except Exception as e:
        #     server_log.info('Exception raised in server when receiving message from client: {}'.format(repr(e)))
        #     raise e
        finally:
            self.msg_buffer = []
            self.msg = ''

    ## MESSAGE HANDLERS:

    def handle_get_client_id(self):
        server_log.info(str(self.client_id) + ': sending client id')
        self.push(client_api["set_client_id"] + client_api["delimiter"] + str(self.client_id) + client_api["terminator"])

    def handle_ready(self):
        server_log.info(str(self.client_id) + ': client ready, sending test request')
        self.push(client_api["set_client_id"] + client_api["delimiter"])

    def handle_heartbeat(self):
        server_log.info(str(self.client_id) + ': heartbeat received')


if __name__ == '__main__':
    server = None
    try:
        server = Server(config["host"], config["port"])
    except KeyboardInterrupt:
        server_log.info('Keyboard interrupt: Shutting server down...')
    #except Exception as e:
    #    print server_log.info('Exception raised at runtime: {}'.format(repr(e)))
    #    raise e
    finally:
        if server:
            server.write_report()
            server.close()