__author__ = 'Wade Pentz'

import asyncore
import asynchat
import socket
import os
import time
import logging
import argparse
from sys import platform
from multiprocessing import Process
from config import config
from client_api import client_api
from logs import client_log, file_formatter

# Utility constants
BYTES_PER_MEGABYTE = 1024 * 1024
# For finding performance stats in 'ps aux' output
COLUMN_PID = 1
COLUMN_CPU = 2
COLUMN_MEM = 3

"""client.py

Client class

Describe arguments - especially units (MB for chunk and file size, time in seconds)

More details
Example of usage:
Stuff

"""

class Client(asynchat.async_chat):
    """A generic client class that handles connecting to the server including sending/receiving basic messages
    to/from the server. Designed to be inherited to create clients that run specific tests while reporting to the server.

    Abstracts - When inheriting this class the following must be defined:
        run_tests (method): Implement to run desired client tests or behaviors that occur once connected to a host.

    Args:
        host (int): test server address to connect to
        port (int): port test server is listening on

    Note: Any new commands expected from the server must be given handler methods and added to self.msg_handler.
          This dictionary can be appended to using self.msg_handler.update() in child classes.
    """

    def __init__(self, host, port):
        asynchat.async_chat.__init__(self)
        self.host = host
        self.port = port
        self.client_id = 0
        self.msg_buffer = []
        self.msg = ''
        self.msg_split = []
        self.set_terminator(client_api["terminator"])
        self.init_log_file()
        self.msg_handler = { client_api["set_client_id"]: self.handle_set_id,
                             client_api["run_tests"]: self.handle_run_tests } 
    
    def connect_to_server(self):
        # Connect to server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.host, self.port))
        asyncore.loop(timeout=config["client_timeout"])

    def init_log_file(self):
        """Initializes the client's log file."""
        try:
            os.makedirs(config["client_log_path"])
        except OSError as e:
            if not os.path.isdir(config["client_log_path"]):
                raise e
        client_log_file = logging.FileHandler(config["client_log_path"] + 'client_log_' + 
                                                time.strftime('%Y-%m-%d_%H.%M.%S') + '.txt')
        client_log_file.setLevel(logging.DEBUG)
        client_log_file.setFormatter(file_formatter)
        client_log.addHandler(client_log_file)

    def handle_connect(self):
        client_log.info('Connected to server')
        self.send_get_id()
        self.send_ready()

    def handle_close(self):
        if self.client_id:
            client_log.info('Client id {} shutting down...'.format(self.client_id))
        else:
            client_log.info('Client shutting down...')
        self.close()

    def collect_incoming_data(self, data):
        self.msg_buffer.append(data)

    def found_terminator(self):
        """Processes the incoming message by looking up the handler in the message dictionary."""
        self.msg = ''.join(self.msg_buffer)
        self.msg_split = self.msg.split(client_api["delimiter"])
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
            self.msg_split = []

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

    def send_start(self):
        """Informs the server that the client has started running the test request."""
        self.push(client_api["start"] + client_api["terminator"])

    def send_done(self):
        """Informs the server that the client is done running."""
        self.push(client_api["done"] + client_api["terminator"])

    ## MESSAGE HANDLERS:

    def handle_set_id(self):
        """Sets client_id based on server response"""
        if len(self.msg_split) == 2:
            self.client_id = self.msg_split[1]
            client_log.info('Client id received from server: {}'.format(self.client_id))
        else:
            client_log.info('ERROR: Invalid client id received from server!')
            self.handle_close()

    def handle_run_tests(self):
        """Begins testing at the server's request."""
        client_log.info('Test run request received from server')
        self.run_tests()


class FileWriterClient(Client):
    """Multi-threaded client that writes a file while reporting performance data to the host.
    A heartbeat message is also sent to the server every 5 seconds.

    Args:
        host (int): test server address to connect to
        port (int): port test server is listening on
        run_time (int): number of seconds that the client should run for
        chunk_size (int): size of data "chunks" (in megabytes) that client should write to files
        file_size (int): size of files (in megabytes) that client should write
    """

    def __init__(self, host, port, run_time=config["default_run_time"], 
            chunk_size=config["default_chunk_size"], file_size=config["default_file_size"]):
        Client.__init__(self, host, port)
        self.run_time = run_time
        self.chunk_size = chunk_size
        self.file_size = file_size
        self.chunk = b'\x5a' * self.chunk_size * BYTES_PER_MEGABYTE
        self.chunks_per_file = int(self.file_size / self.chunk_size)
        self.remaining_mb = int(self.file_size % self.chunk_size)
        self.remaining_chunk = b'\x5a' * self.remaining_mb * BYTES_PER_MEGABYTE
        self.tests_done = False
        self.threads = []
        if not self.check_chunk_size() or not self.check_file_rollover():
            raise ValueError('Invalid client configuration!')

    def handle_close(self):
        Client.handle_close(self)
        self.tests_done = True
        for thread in self.threads:
            thread.terminate()

    def run_tests(self):
        """Kicks off threads for the following processes: 
            - Writing the file as specified
            - Periodically sending a heartbeat to the server
            - Periodically sending performance stats to the server

        These processes are all terminated when client closes."""
        self.send_file_stats()
        client_log.info('Running tests...')
        self.send_start()
        test_end_time = time.time() + self.run_time
        file_write_thread = Process(target=self.write_file)
        file_write_thread.start()
        self.threads.append(file_write_thread)
        heartbeat_thread = Process(target=self.send_heartbeat)
        heartbeat_thread.start()
        self.threads.append(heartbeat_thread)
        send_stats_thread = Process(target=self.send_performance_stats, args=(file_write_thread.pid,))
        send_stats_thread.start()
        self.threads.append(send_stats_thread)
        while not self.tests_done and time.time() < test_end_time:
            time.sleep(config["done_check_period"])
        self.send_done()
        self.handle_close()

    def check_chunk_size(self):
        """Verifies that the provided chunk_size meets the spec (minimum of 10 MB)"""
        if self.chunk_size < config["chunk_size_minimum"]:
            client_log.info('ERROR: Chunk size is below minimum of {} MB'.format(config["chunk_size_minimum"]))
            return False
        if self.chunk_size > self.file_size:
            client_log.info('ERROR: Chunk size is larger than file size'.format(config["chunk_size_minimum"]))
            return False
        return True

    def check_file_rollover(self):
        """Checks if the file will rollover twice with the given arguments based on a timed performance measurement."""
        client_log.info('Checking if files will rollover twice with the given client parameters...')
        file_name = config["client_file_path"] + 'client_test_file'
        try:
            with open(file_name, 'ab') as f:
                start_time = time.time()
                f.write(self.chunk)
                chunk_write_time = time.time() - start_time
                start_time = time.time()
                f.write(self.remaining_chunk)
                remaining_chunk_write_time = time.time() - start_time
                file_roll_time = chunk_write_time * self.chunks_per_file + remaining_chunk_write_time
        except IOError:
            client_log.info('ERROR: Could not open test file to write!')
            self.handle_close()
        except Exception:
            client_log.info('ERROR: Unknown error during test file write!')
            self.handle_close()
        finally:
            os.remove(file_name)
        # Convert to seconds and check against 2-file-roll requirement
        if file_roll_time * 2 < self.run_time:
            return True
        else:
            return False

    def write_file(self):
        """Thread: Writes data to a file in chunks as configured by the input arguments for the client.
        When a file of size defined by the file_size argument has completed writing"""
        try:
            os.makedirs(config["client_file_path"])
        except OSError:
            if not os.path.isdir(config["client_file_path"]):
                client_log.info('ERROR: Could not create nor find client file directory.')
                self.handle_close()

        file_count = 0
        while not self.tests_done:
            file_name = config["client_file_path"] + 'client_' + str(self.client_id) + '_' + str(file_count) + \
                '_' + time.strftime('%Y-%m-%d_%H.%M.%S') 
            try:
                with open(file_name, 'ab') as f:
                    for chunk in range(self.chunks_per_file):
                        f.write(self.chunk)
                    f.write(self.remaining_chunk)
                    client_log.info('Finished writing {} MB file! Starting new file write...'.format(self.file_size))
                    self.send_file_rollover()
            except IOError:
                client_log.info('ERROR: Could not open file to write!')
                self.handle_close()
            except Exception:
                client_log.info('ERROR: Unknown error during file write!')
                self.handle_close()
            file_count += 1

    ## MESSAGE SENDERS:

    def send_heartbeat(self):
        """Thread: Sends a heartbeat message to the server every 'heartbeat_period' seconds. No response expected."""
        while not self.tests_done:
            time.sleep(config["heartbeat_period"])
            client_log.info('Heartbeat sent to server')
            self.push(client_api["heartbeat"] + client_api["terminator"])

    def send_performance_stats(self, pid):
        """Thread: Sends performance data of the file write operation to the server every 'perf_stats_period' seconds"""
        while not self.tests_done:
            time.sleep(config["perf_stats_period"])
            if platform == "linux" or platform == "linux2" or platform == "darwin":
                # Get %CPU and %MEM stats for the file write process using unix 'ps aux' command
                with os.popen('ps aux') as f:
                    for line in f:
                        if line.split()[COLUMN_PID] == str(pid):
                            cpu = line.split()[COLUMN_CPU]
                            mem = line.split()[COLUMN_MEM]
                            self.push(client_api["send_perf_stats"] + client_api["delimiter"] + 
                                cpu + client_api["delimiter"] + 
                                mem + client_api["terminator"])
                            client_log.info('File write performance stats sent to server. ' \
                                '(CPU={} MEM={})'.format(cpu, mem))
                            return
                    client_log.info('WARNING: Could not find pid for file write process in process list! ' \
                        'Process stats not sent to server.')
            else:
                client_log.info('WARNING: Cannot get file write process statistics on non-Unix-based platforms.')     

    def send_file_rollover(self):
        self.push(client_api["file_rollover"] + client_api["terminator"])

    def send_file_stats(self):
        """Sends chunk size and file size to server for reporting."""
        client_log.info('File parameters sent to server.')
        self.push(client_api["send_file_stats"] + client_api["delimiter"] + str(self.chunk_size) +
            client_api["delimiter"] + str(self.file_size) + client_api["terminator"])


if __name__ == '__main__':
    # Create FileWriterClient that writes files based on the arguments provided.
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--runtime', dest='run_time', default=config["default_run_time"], type=int,
                        help='total allowed client run time')
    parser.add_argument('-c', '--chunksize', dest='chunk_size', default=config["default_chunk_size"], type=int,
                        help='file size to write')
    parser.add_argument('-f', '--filesize', dest='file_size', default=config["default_file_size"], type=int,
                        help='file size to write')
    args = parser.parse_args()

    client = None
    client = FileWriterClient(config["host"], config["port"], args.run_time, args.chunk_size, args.file_size)
    try:
        client.connect_to_server()
    except KeyboardInterrupt:
        client_log.info('Keyboard interrupt: Shutting client down...')
    except Exception as e:
       print client_log.info('Exception raised at runtime: {}'.format(repr(e)))
       raise e
    finally:
        if client:
            client.close()


