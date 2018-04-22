__author__ = 'Wade Pentz'
import logging

# Global logging handlers
console_formatter = logging.Formatter('%(module)ls - %(asctime)s - %(message)s', datefmt='%H:%M:%S')
file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d(%H:%M:%S)')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(console_formatter)

server_log = logging.getLogger('server_Log')
server_log.setLevel(logging.DEBUG)
server_log.addHandler(console)

client_log = logging.getLogger('client_log')
client_log.setLevel(logging.DEBUG)
client_log.addHandler(console)


