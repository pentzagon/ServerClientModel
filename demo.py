__author__ = 'Wade Pentz'

import subprocess
from server import Server
from config import config

"""demo.py

This script establishes a server then spins up 3 differently-configured clients to connect to 
and run file write tests while reporting to that server.
"""

def spin_up_client(delay=0, run_time=config["default_run_time"], chunk_size=config["default_chunk_size"], 
    file_size=config["default_file_size"]):
    """Uses subprocess to launch a file write client with the given parameters."""
    subprocess.call("sleep {} && python client.py -r {} -c {} -f {}".format(
        delay, run_time, chunk_size, file_size), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

if __name__ == '__main__':
    # Spin up some clients
    spin_up_client(delay=1, run_time=15, chunk_size=10, file_size=100)
    spin_up_client(delay=3, run_time=5, chunk_size=15, file_size=80)
    spin_up_client(delay=6, run_time=10, chunk_size=25, file_size=50)

    # Start the server
    server = None
    try:
        server = Server(config["host"], config["port"])
    except KeyboardInterrupt:
        server_log.info('Keyboard interrupt: Shutting server down...')
    except Exception as e:
       print server_log.info('Exception raised at runtime: {}'.format(repr(e)))
       raise e
    finally:
        if server:
            server.write_report()
            server.close()