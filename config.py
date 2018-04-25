__author__ = 'Wade Pentz'

"""A dictionary that stores all server/client configuration information."""
config = {
    # Log configuration
    "server_log_path": './server_logs/',
    "client_log_path": './client_logs/',

    # Network configuration
    "host": 'localhost',
    "port": 1234,
    "server_timeout": 0.1,
    "server_loop_count": 1,
    "client_timeout": 0.5,
    "first_client_id": 100,

    # Client configuration
    "client_file_path": './client_files/',
    "default_run_time": 30,
    "default_chunk_size": 10,
    "default_file_size": 50,
    "heartbeat_period": 5,
    "perf_stats_period": 10,
    "done_check_period": 0.5,
    "chunk_size_minimum": 10,
}
