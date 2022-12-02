from __future__ import print_function
import os, sys

def log(*items):
    print(*items)

def log_error(*items):
    print(*items, file=sys.stderr)

def get_logs_directory():
    return os.environ.get('APP_LOGS', '/tmp')

def get_root_directory():
    if "APP_ROOT" not in os.environ:
        sys.exit('APP_ROOT env var found. Please set it to the root of your app')
    return os.environ['APP_ROOT']

def run_command(command):
    log('>', command)
    return os.WEXITSTATUS(os.system(command))

