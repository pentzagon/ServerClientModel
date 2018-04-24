# ServerClientModel

## General Description:
Stuff to fill in here.

## Client/Server protocol:
Messages between the server and client are defined in client_api.py and can optionally be sent with arguments. Arguments are delimited by ':' (as defined in client_api.py). The first (or 0th) argument for every message is the command. Each command is a string defined client_api.py and is expected to be handled in a server and/or client class.

## Notes:
* File writes 
* In violation of PEP8 I used a 120-character column limit instead of 80. 120 is suitable for modern resolutions.

## ToDo list:
* Create setup file that pip installs all packages if any non-standard libraries are used.
* Flesh out server comments
* Write unit tests (required) (file for each of client and server unit tests??)
* Lint all files. Pylint?
* Keep track of client data to provide details in log (average cpu usage, etc.) on server side
* Calculations for 2 file rollovers, performance data, etc (helpers.py)
* Write test/script to spin up some clients