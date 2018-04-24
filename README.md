# ServerClientModel
### A client/server model in Python

## Client/Server protocol:
Messages between the server and client are defined in client_api.py and can optionally be sent with arguments. Arguments are delimited by ':' (as defined in client_api.py). The first (or 0th) argument for every message is the command. Each command is a string defined client_api.py and is expected to be handled in a server and/or client class.

## Notes:
* In violation of PEP8 I used a 120-character column limit instead of 80. 120 is suitable for modern resolutions.

## ToDo list:
* Create setup file that pip installs all packages if any non-standard libraries are used.
* Flesh out server comments
* Write unit tests (required) (file for each of client and server unit tests??)
* Test basic client heartbeat
* Test client closing early (logging, handling)
* Lint all files. Pylint?
* Keep track of client data to provide details in log (average cpu usage, etc.) on server side
* Calculations for 2 file rollovers, performance data, etc (helpers.py)
* Close all clients processes upon exit
* Figure out how to end all threads in client.