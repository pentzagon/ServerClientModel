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

The Server class uses the asyncore library to set up a local, asynchronous server 
that records test results sent by connected clients. A ClientHandler object is created 
for each new client that connects. Clients communicate with the server using a 
string-based messaging protocol that is defined in client_api.py. Clients are also
tracked using sequential client ids that are assigned upon connection and sent to the
client upon the client's request.

The server logs client connections and messages to the console and to a file saved 
to ./server_logs named 'server_log_<date&time>'. Once all clients have finished
running, the server writes a report displaying statistics for each client including
how long they ran, file write information, performance stats, and status into the 
log file. If clients drop out before finishing that is logged.

Example usage of this class is shown in the "if __name__ == '__main__':" block at
the end of this file.

"""

class Server(asyncore.dispatcher):
    """Server class that logs performance data from multiple, concurrent test clients.

    Args:
        host (str): address where test server will run.
        port (int): network port the server will run on.
    """

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.client_id = config["first_client_id"]
        self.client_list = {}
        self.start_time = ''
        self.end_time = ''
        self.init_log_file()
        self.init_server_socket()

    def init_log_file(self):
        """Initializes the server's log file for client data."""
        try:
            os.makedirs(config["server_log_path"])
        except OSError:
            if not os.path.isdir(config["server_log_path"]):
                raise
        server_log_file = logging.FileHandler(
            config["server_log_path"] + 'server_log_' + time.strftime('%Y-%m-%d_%H.%M.%S') + '.txt')
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

    def start_server(self):
        self.start_time = time.strftime('%Y-%m-%d_%H:%M:%S')
        self.run_loop()

    def handle_accept(self):
        """Handles a client connection - Creates a ClientHandler instance for it.
        The ClientHandler is stored according to client_id in the client_list dictionary."""
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            server_log.info('Client connection from {}, assigning client id {}'.format(repr(addr), self.client_id))
            handler = ClientHandler(sock, addr, self.client_id)
            self.client_list.update({self.client_id: handler})
            self.client_id += 1

    def handle_close(self):
        server_log.info('Server shutting down...')
        self.close()

    def run_loop(self):
        """Run asyncore.loop until all clients are closed"""
        server_log.info('Server now accepting client connections.')
        while not self.clients_done():
            asyncore.loop(timeout=config["server_timeout"], count=config["server_loop_count"])

    def clients_done(self):
        """Returns True if all clients have completed their tests and at least one client has connected."""
        if not self.client_list:
            return False
        elif len(asyncore.socket_map) > 1:
            return False
        else:
            return True

    def write_report(self):
        """Writes out a report that displays data for all clients that ran."""
        self.end_time = time.strftime('%Y-%m-%d_%H:%M:%S')
        server_log.info('')
        server_log.info('=========================================================')
        server_log.info('All test clients completed!')
        server_log.info('    Start time: {}'.format(self.start_time))
        server_log.info('    End time:   {}'.format(self.end_time))
        server_log.info('')
        server_log.info('Total of {} client(s) ran. Data for each client:'.format(len(self.client_list)))
        for client in self.client_list.values():
            server_log.info('---------------------------------------------------------')
            server_log.info('  Client {}'.format(client.client_id))
            server_log.info('    Test status:   {}'.format(client.status))
            server_log.info('    Time ran:      {:.2f} sec'.format(client.time_ran)) 
            server_log.info('    Avg CPU usage: {:.2f}%'.format(client.cpu_avg))
            server_log.info('    Avg MEM usage: {:.2f}%'.format(client.mem_avg))
            server_log.info('    Files written: {}'.format(client.files_written))
            server_log.info('    File size:     {}'.format(client.file_size))
            server_log.info('    Chunk size:    {}'.format(client.chunk_size))
        server_log.info('=========================================================')
        server_log.info('')


class ClientHandler(asynchat.async_chat):
    """Class instantiated to keep track of each client that connects to the server.

    Args:
        sock (int): socket on which the client is connected.
        addr (int): address on which the client is connected.
        id (int): unique identifier for client.
    """

    def __init__(self, sock, addr, client_id):
        asynchat.async_chat.__init__(self, sock=sock)
        self.addr = addr
        self.client_id = client_id
        self.set_terminator(client_api["terminator"])
        self.start_time = 0
        self.end_time = 0
        self.time_ran = 0
        self.num_stat_reports = 0
        self.cpu_avg = 0
        self.mem_avg = 0
        self.cpu_total = 0
        self.mem_total = 0
        self.chunk_size = 0
        self.file_size = 0
        self.files_written = 0
        self.status = 'NOT STARTED'
        self.msg_buffer = []
        self.msg = ''
        self.msg_split = []
        self.msg_handler = { client_api["get_client_id"]: self.handle_get_client_id,
                             client_api["ready"]: self.handle_ready,
                             client_api["start"]: self.handle_start,
                             client_api["done"]: self.handle_done,
                             client_api["heartbeat"]: self.handle_heartbeat,
                             client_api["send_perf_stats"]: self.handle_perf_stats,
                             client_api["send_file_stats"]: self.handle_file_stats,
                             client_api["file_rollover"]: self.handle_file_rollover, }

    def collect_incoming_data(self, data):
        """Buffer incoming message"""
        self.msg_buffer.append(data)

    def found_terminator(self):
        """Processes the incoming message by looking up the handler in the message dictionary."""
        self.msg = ''.join(self.msg_buffer)
        self.msg_split = self.msg.split(client_api["delimiter"])
        cmd = self.msg_split[0]
        try:
            self.msg_handler[cmd]()
        except KeyError as e:
            server_log.info('Unhandled command received from client id {}: {}'.format(self.client_id, cmd))
        except Exception as e:
            server_log.info('Exception raised in server when receiving message from client: {!r}'.format(e))
            raise e
        finally:
            self.msg_buffer = []
            self.msg = ''
            self.msg_split = []

    def handle_close(self):
        """Sets test status and closes connection."""
        self.end_time = time.time()
        self.time_ran = self.end_time - self.start_time
        if self.status != 'PASS':
            server_log.info('Client {} aborted!'.format(self.client_id))
            self.status = 'ABORTED'
        self.close()

    ## MESSAGE HANDLERS:

    def handle_get_client_id(self):
        server_log.info(str(self.client_id) + ': Sending client id')
        self.push(client_api["set_client_id"] + client_api["delimiter"] + str(self.client_id) + client_api["terminator"])

    def handle_ready(self):
        server_log.info(str(self.client_id) + ': Client ready, sending test request')
        self.push(client_api["run_tests"] + client_api["terminator"])

    def handle_start(self):
        server_log.info(str(self.client_id) + ': Client started running tests')
        self.status = 'RUNNING'
        self.start_time = time.time()

    def handle_done(self):
        server_log.info(str(self.client_id) + ': Client finished running tests')
        self.status = 'PASS'
        self.handle_close()

    def handle_heartbeat(self):
        server_log.info(str(self.client_id) + ': Heartbeat received')

    def handle_perf_stats(self):
        if len(self.msg_split) == 3:
            cpu = self.msg_split[1]
            mem = self.msg_split[2]
            server_log.info(str(self.client_id) + ': Performance stats received. CPU: {} Mem: {}'.format(cpu, mem))
        else:
            server_log.info(str(self.client_id) + ': Invalid performance stats received')
            return False
        self.num_stat_reports += 1
        self.cpu_total += float(cpu)
        self.mem_total += float(mem)
        self.cpu_avg = self.cpu_total / self.num_stat_reports
        self.mem_avg = self.mem_total / self.num_stat_reports
        return True

    def handle_file_stats(self):
        if len(self.msg_split) == 3:
            self.chunk_size = int(self.msg_split[1])
            self.file_size = int(self.msg_split[2])
            server_log.info(str(self.client_id) + ': File stats received. \
                Chunk size: {} File size: {}'.format(self.chunk_size, self.file_size))
            return True
        else:
            server_log.info(str(self.client_id) + ': Invalid file stats received')
            return False

    def handle_file_rollover(self):
        server_log.info(str(self.client_id) + ': File rolled over')
        self.files_written += 1


if __name__ == '__main__':
    server = None
    try:
        server = Server(config["host"], config["port"])
        server.start_server()
    except KeyboardInterrupt:
        server_log.info('Keyboard interrupt: Shutting server down...')
    except Exception as e:
       print server_log.info('Exception raised at runtime: {}'.format(repr(e)))
       raise e
    finally:
        if server:
            server.write_report()
            server.close()
