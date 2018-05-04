# ServerClientModel

## General Description:
This module consists of two major parts: a server and a client. The server is designed to handle up to five concurrent test clients and closes itself once all connected clients have closed. The clients designed for this module extend a generic client class that handles connecting to the server. These extended clients perform a file write per the class input arguments while reporting performance data and heartbeats to the server. Each of these processes (file write, performance data, and heartbeats) gets their own thread which is managed by the Python multiprocessing library.

The server and client communicate with eachother using a string-based protocol over sockets based on the standard asyncore and asynchat Python modules. See the "Client/Server Protocol" section for further details on the protocol. 

Additional information on how each piece works can be found in detailed doc strings included at the top of each file.

## To Demo:
Enter 'python demo.py' in the command line in this directory to run a demo that spins up a server and a few clients with varying file size, chunk size, and run time arguments.

## Client Connection Sequence Diagram:
__Server      <->      Client__  
            <-- connect  
            <-- get client id  
client id   -->  
            <-- ready  
start tests -->  
            <-- start  
             .  
             .  (runs tests)  
             .  
            <-- done  

## Client/Server Protocol:
Messages between the server and client are defined in client_api.py and can optionally be sent with arguments. Arguments are delimited by ':' (as defined in client_api.py). The first (or 0th) argument for every message is the command. Each command is a string defined in client_api.py that is expected to be handled in a server and/or client class.

_Example: When a client sends its performance statistics to the server the command takes this form "send_stats:cpu_stat:mem_stat" (where cpu_stat and mem_stat are actual performance numbers)._

## Future Improvements:
_All requirements for this project have been fulfilled as far as I know. Below is a list of improvements I would make if I had additional time to work on it._
* Implement Flask-based server and use RESTful-like API to exchange messages between the client and server.
* Improved accuracy of CPU and memory usage of file writing process. Ex: factor in number of cores for CPU usage, grab actual byte-memory usage and compare to total memory available.
* Extended unit and integration tests. This would require modifying the current class methods to return more status information.

## Note:
In violation of PEP8 I used a 120-character column limit instead of 80. 120 is suitable for modern resolutions.
