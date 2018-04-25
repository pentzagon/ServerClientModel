__author__ = 'Wade Pentz'

import server
import client

"""main.py

This establishes a server then spins up 3 differently-configured clients to connect to 
and run file write tests while reporting to that server.
"""

if __name__ == '__main__':
    pass
    # server = None
    # try:
    #     server = Server(config["host"], config["port"])
    # except KeyboardInterrupt:
    #     server_log.info('Keyboard interrupt: Shutting server down...')
    # except Exception as e:
    #    print server_log.info('Exception raised at runtime: {}'.format(repr(e)))
    #    raise e
    # finally:
    #     if server:
    #         server.write_report()
    #         server.close()