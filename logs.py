__author__ = 'Wade Pentz'
import logging

# Include date in text file logs but not on console.
# Text file logs are set up upon class instantiation (both server and client).
console_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d(%H:%M:%S)')

# Print all log messages to the console window
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(console_formatter)

# Logger for server side
server_log = logging.getLogger('server_Log')
server_log.setLevel(logging.DEBUG)
server_log.addHandler(console)

# Logger for client side
client_log = logging.getLogger('client_log')
client_log.setLevel(logging.DEBUG)
client_log.addHandler(console)

