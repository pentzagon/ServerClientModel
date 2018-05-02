# ServerClientModel

## General Description:
Stuff to fill in here.

Handles clients dropping out well.
Chunk size must be greater than 10MB, but less than the file size.

client class designed to be extended.

## To Demo:
Enter 'python demo.py' in the command line in this directory to run a demo that spins up a server and a few clients with varying file size, chunk size, and run time arguments.

## Client/Server Protocol:
Messages between the server and client are defined in client_api.py and can optionally be sent with arguments. Arguments are delimited by ':' (as defined in client_api.py). The first (or 0th) argument for every message is the command. Each command is a string defined client_api.py and is expected to be handled in a server and/or client class.

_Example: When a client sends its performance statistics to the server the command takes this form "send_stats:cpu_stat:mem_stat" where cpu_stat and mem_stat are the actual data points._

## Notes:
* In violation of PEP8 I used a 120-character column limit instead of 80. 120 is suitable for modern resolutions.

## Future Improvements:
* Implement Flask-based server and use RESTful-like API to exchange messages between the client and server.
* Improved accuracy of CPU and memory usage of file writing process. Ex: factor in number of cores for CPU usage, grab actual byte-memory usage and compare to total memory available.

## ToDo List:
* Create setup file that pip installs all packages if any non-standard libraries are used. (not currently needed)
* Flesh out general comments at top of client.py and server.py
* Write unit tests (required) (file for each of client and server unit tests??)
* Lint all files. Pylint? Add note in documentation.
* Write test/script to spin up some clients (main.py)
* Convert dicitonaries to objects?
