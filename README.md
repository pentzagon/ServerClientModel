# ServerClientModel

## General Description:
Stuff to fill in here.

Handles clients dropping out well.
Chunk size must be greater than 10MB, but less than the file size.

## Client/Server P{rotocol:
Messages between the server and client are defined in client_api.py and can optionally be sent with arguments. Arguments are delimited by ':' (as defined in client_api.py). The first (or 0th) argument for every message is the command. Each command is a string defined client_api.py and is expected to be handled in a server and/or client class.

## Notes:
* File writes 
* In violation of PEP8 I used a 120-character column limit instead of 80. 120 is suitable for modern resolutions.

## Future Improvements:
* Implement Flask-based server and use RESTful-like API to exchange messages between the client and server.
* Improved accuracy of CPU and memory usage of file writing process.

## ToDo List:
* Create setup file that pip installs all packages if any non-standard libraries are used. (not currently needed)
* Flesh out server comments
* Write unit tests (required) (file for each of client and server unit tests??)
* Lint all files. Pylint?
* Calculations for 2 file rollovers (helpers.py?)
* Write test/script to spin up some clients (main.py)
* Add client transmission of file size and chunk size to server for report.
* Figure out why file sizes are all over the place and inconsistent CPU/MEM stats.
