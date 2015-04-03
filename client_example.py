#!/usr/bin/env python
import socket
import hashlib
import time


def hash(input):
    return(hashlib.sha256(input).hexdigest())

def TCP_client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        data = {}
        data = sock.recv(1024*16)
    finally:
        sock.close()
        return data

print(TCP_client("localhost",16260,"1,user,"+hash("password"+str(time.time())[0:8]+"start")+",start"))