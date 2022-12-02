import os, sys

# get rid of grpc fork-support warnings
os.environ["GRPC_POLL_STRATEGY"] = "poll"

# setup env
libdir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(libdir, "p4app/src"))
os.environ["APP_ROOT"] = os.path.abspath(os.path.join(libdir, "../"))
os.environ["APP_LOGS"] = os.path.join(os.environ["APP_ROOT"], "logs")
os.environ["APP_TEST"] = os.path.join(os.environ["APP_LOGS"], "test")

# create the logs dir if not there
if not os.path.exists(os.environ["APP_LOGS"]):
    os.makedirs(os.environ["APP_LOGS"])