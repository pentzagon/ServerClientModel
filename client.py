__author__ = 'Wade Pentz'

import asyncore
import asynchat
import socket
import os
import time
import logging
import argparse
from multiprocessing import Process
from config import config
from client_api import client_api
from logs import client_log, file_formatter

"""client.py

Client class

More details

Example of usage:
Stuff

"""

class Client(asynchat.async_chat):
    """Multi-threaded client that writes a file while reporting performance data to the host.

    Abstracts - When inheriting this class the following must be defined:
        msg_handler (dict): A handler used to convert string commands from the server into method calls.
        run_tests (method): Implement to run desired client tests or behaviors that occur once connected to as host.

    Args:
        host (int): test server address to connect to.
        port (int): port test server is listening on.
    """

    def __init__(self, host, port):
        asynchat.async_chat.__init__(self)
        self.host = host
        self.port = port
        self.client_id = 0
        self.msg_buffer = []
        self.msg = ''
        # TODO - delete connected?
        self.connected = False
        self.set_terminator(client_api["terminator"])
        self.init_log_file()
        # When inheriting add handlers to self.msg_handler for expected server messages in __init__().
        # e.g. self.msg_handler.update({'expected_command': handler_function})
        self.msg_handler = { client_api["set_client_id"]: self.handle_set_id,
                             client_api["set_client_id"]: self.handle_run_tests } 
    
    def connect_to_server(self):
        # Connect to server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.host, self.port))
        # TODO - delete
        client_log.info('executing .loop()')
        asyncore.loop(timeout=config["client_timeout"])

    def init_log_file(self):
        """Initializes the client's log file."""
        try:
            os.makedirs(config["client_log_path"])
        except OSError:
            if not os.path.isdir(config["client_log_path"]):
                raise
        client_log_file = logging.FileHandler(config["client_log_path"] + 'client_log_' + 
                                                time.strftime('%Y-%m-%d_%H.%M.%S') + '.txt')
        client_log_file.setLevel(logging.DEBUG)
        client_log_file.setFormatter(file_formatter)
        client_log.addHandler(client_log_file)

    def handle_connect(self):
        client_log.info('Connected to server')
        # TODO - delete?
        self.connected = True
        self.send_get_id()
        # TODO - delete this?
        #self.run_tests()

    def handle_close(self):
        if self.client_id:
            client_log.info('Client id {} shutting down...'.format(self.client_id))
        else:
            client_log.info('Client shutting down...')
        self.close()

    def collect_incoming_data(self, data):
        # TODO - remove this print
        client_log.info('collect_incoming_data {}'.format(data))
        self.msg_buffer.append(data)

    def found_terminator(self):
        """Processes the incoming message by looking up the handler in the message dictionary."""
        self.msg = ''.join(self.msg_buffer)
        client_log.info('Received message from server: {}'.format(self.msg))
        cmd = self.msg.split(client_api["delimiter"])[0]
        try:
            self.msg_handler[cmd]()
        except KeyError as e:
            client_log.info('Unhandled message received from the server. cmd={}'.format(cmd))
        except Exception as e:
            client_log.info('Exception raised in client when running found_terminator: {}'.format(repr(e)))
            raise e
        finally:
            self.msg_buffer = []
            self.msg = ''

    def run_tests(self):
        """Runs desired client tests. This method must be overridden in any child class."""
        raise NotImplementedError

    ## MESSAGE SENDERS:

    def send_get_id(self):
        """Requests client_id from server"""
        self.push(client_api["get_client_id"] + client_api["terminator"])

    def send_ready(self):
        """Informs the server that the client is ready to receive a test request."""
        self.push(client_api["ready"] + client_api["terminator"])

    def send_done(self):
        """Informs the server that the client is done running."""
        self.push(client_api["done"] + client_api["terminator"])

    ## MESSAGE HANDLERS:

    def handle_set_id(self):
        """Sets client_id based on server response"""
        self.client_id = self.msg.split(client_api["delimiter"])[1]
        client_log.info('Client id received from server: {}'.format(self.client_id))

    def handle_run_tests(self):
        """Begins testing at the server's request."""
        client_log.info('Test request received from server.')
        self.run_tests()


class FileWriterClient(Client):
    """Multi-threaded client that writes a file while reporting performance data to the host.
    A heartbeat message is also sent to the server every 5 seconds."""

    def __init__(self, host, port, run_time=config["default_run_time"], 
                    chunk_size=config["default_chunk_size"], file_size=config["default_file_size"]):
        Client.__init__(self, host, port)
        self.run_time = run_time
        self.chunk_size = chunk_size
        self.file_size = file_size
        self.tests_done = False
    #    self.msg_handler.update({client_api["get_client_id"]: self.get_})

    def handle_close(self):
        Client.handle_close(self)
        self.tests_done = True

    def run_tests(self):
        """Runs file write test. Also kicks off processes for sending heartbeat
        and performance stats to the server periodically."""
        client_log.info('Running tests...')
        test_end_time = time.time() + self.run_time
        heartbeat_thread = Process(target=self.send_heartbeat)
        heartbeat_thread.start()
        #Process(target=self.send_performance_stats).start()
        #Process(target-self.write_file).start()
        while not self.tests_done and time.time() < test_end_time:
            time.sleep(config["done_check_period"])
        heartbeat_thread.terminate()
        self.handle_close()
        # TODO - Delete this?
        # heartbeat_thread.join()

    def check_file_rollover(self):
        """Checks if the file will rollover twice with the given arguments based on a performance measurement."""
        pass

    ## MESSAGE SENDERS:

    def send_heartbeat(self):
        """Thread: Sends a heartbeat message to the server every 'heartbeat_period' seconds. No response expected."""
        while not self.tests_done:
            time.sleep(config["heartbeat_period"])
            client_log.info('Heartbeat sent to server.')
            self.push(client_api["heartbeat"] + client_api["terminator"])
        #Process(target=self.send_heartbeat).start()

    def send_performance_stats(self):
        """Thread: Sends performance data of the file write operation to the server every 'perf_stats_period' seconds"""
        while not self.tests_done:
            time.sleep(config["perf_stats_period"])
            client_log.info('Heartbeat sent to server.')
            self.push(client_api["send_perf_stats"] + client_api["terminator"])


if __name__ == '__main__':
    # Create FileWriterClient that writes files based on the arguments provided.
    client = None

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--runtime', dest='run_time', default=15, type=int,
                        help='total allowed client run time')
    parser.add_argument('-c', '--chunksize', dest='chunk_size', default=50, type=int,
                        help='file size to write')
    parser.add_argument('-f', '--filesize', dest='file_size', default=100, type=int,
                        help='file size to write')
    args = parser.parse_args()

    client = FileWriterClient(config["host"], config["port"], args.run_time, args.chunk_size, args.file_size)

    try:
        #client = FileWriterClient(config["host"], config["port"], args.run_time, args.chunk_size, args.file_size)
        client.connect_to_server()
        # time.sleep(1)
        # if client.connected:
        #     client.run_tests()
        # else:
        #     client_log.info('Client never connected to server. Quitting...')
    except KeyboardInterrupt:
        client_log.info('Keyboard interrupt: Shutting client down...')
    #except Exception as e:
    #    print client_log.info('Exception raised at runtime: {}'.format(repr(e)))
    #    raise e
    finally:
        client.close()
        

