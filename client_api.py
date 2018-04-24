"""Dictionary defining messages that can be sent between the server/client and delimiters."""
client_api = {
    # Control flow
    "terminator": '\n',
    "delimiter": ':',
    
    # Client to server messages
    "get_client_id": 'get_cid',
    "ready": 'ready',
    "done": 'done',
    "heartbeat": 'hb',
    "send_perf_stats": 'send_stats',
    "file_rollover": 'file_roll',

    # Server to client messages
    "set_client_id": 'set_cid',
    "run_tests": 'run_tests',
}