__author__ = 'Wade Pentz'

import subprocess
from multiprocessing import Process
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
    client1 = Process(target=spin_up_client, args=(2, 20, 10, 100))
    client1.start()
    client2 = Process(target=spin_up_client, args=(4, 12, 15, 80))
    client2.start()
    client3 = Process(target=spin_up_client, args=(6, 15, 25, 50))
    client3.start()

    # Start the server
    server = None
    try:
        server = Server(config["host"], config["port"])
    except KeyboardInterrupt:
        print('Keyboard interrupt: Shutting server down...')
    except Exception as e:
        print('Exception raised at runtime: {}'.format(repr(e)))
        raise e
    finally:
        if server:
            server.write_report()
            server.close()
        client1.terminate()
        client2.terminate()
        client3.terminate()