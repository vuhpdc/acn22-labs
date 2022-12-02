import os, sys
from datetime import datetime

def ip(iface="eth0"):
    """
    Retrieve the first ip address assigned to an interface
    """
    return os.popen('ip addr show %s' % iface).read().split("inet ")[1].split("/")[0] # yeah, i know... right?

def rank():
    """
    Retrieve the rank of a worker, assumed to be found at sys.argv[1]
    Throws and exception if an integer cannot be parsed from sys.argv[1]
    """
    rank.val = None
    if rank.val == None:
        rank.val = int(sys.argv[1])
    return rank.val

def PrintUsage():
    print("usage: python worker.py <rank>")

def GetRankOrExit():
    """
    Retrieve the rank of a worker or exist gracefully with usage message
    """
    try:
        return rank()
    except:
        PrintUsage()
        sys.exit(1)

def Log(*args):
    """
    Log a timestamped message to stdout
    """
    now = datetime.now()
    ts = ('%02d:%02d:%02d.%06d' %
          (now.hour, now.minute, now.second, now.microsecond))
    print("[W][%s][%s]" % (ip(), ts), *args)