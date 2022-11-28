import socket
import random
import time

def send(soc, data, addr):
    """ Send `data` to `addr` using socket `soc` """
    soc.sendto(data, addr)

def receive(soc, nbytes):
    """ Receive `nbytes` bytes from socket `soc` """
    return soc.recvfrom(nbytes)

def unreliable_send(soc, data, addr, sleep=2, p=0.3):
    """
    Send 'data' to 'addr' using socket 'soc' with probability 'p' to sleep or drop the packet
    if 'sleep' is a positive integer:
        the packet has probability 'p' to be delayed by 'sleep' seconds
    if 'sleep' is 0 or negative:
        the packet has probability 'p' to be dropped
    if probability is 0, nothing happens
    """
    if p and random.random() < p:
        if sleep < 1:
            return
        time.sleep(sleep)
    soc.sendto(data, addr)
    #
    # if random.random() < sleep_probability:
    #     time.sleep(sleep_time)
    # soc.sendto(data, addr)

def unreliable_receive(soc, nbytes, p=0.3):
    """
    Receive `nbytes` bytes from socket `soc` with probability 'p'
    If 'p' is a positive value, a timeout exception is raised with probability 'p',
    regardless of the timeout status of the socket, effectively "dropping" the packet
    """
    res = soc.recvfrom(nbytes)
    if p and random.random() < p:
        raise socket.timeout
    return res