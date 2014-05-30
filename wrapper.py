#!/usr/bin/env python
import subprocess
import sys
import time
import re
import socket
import threading
import SocketServer

def regexmatch2(text,regex):
    match = regex.match(text)
    if not match:
        return("")
    (matcho,) = match.groups()
    return matcho

global startzom
def startzom():
    isonline = checkzom()
    if isonline=="OFF-LINE":
        print("STARTED")
        p = subprocess.Popen("/home/redm/Steam/SteamApps/common/ProjectZomboid/projectzomboid-dedi-server.sh")
        while p.wait():
            #return("DONE")
            pass
        
global killzom
def killzom():
    isonline = checkzom()
    if isonline=="ON-LINE":
        out = subprocess.check_output("ps aux | grep \"java -D\"", shell=True)
        pid = regexmatch2(out,re.compile(r'.+?     (.+?) .*'))
        subprocess.call(["kill", pid])
        print("KILLED")
        return("KILLED")
    else:
        return("NO SERVER")
    
global checkzom
def checkzom():
    out = subprocess.check_output('ps aux | grep "java -D"', shell=True)
    pidcount = len(out.split("\n"))
    if pidcount==3:
        return("OFF-LINE")
    elif pidcount==4:
        return("ON-LINE")
    return(len(out.split("\n")))
    
    
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        if data=="start":
            response = "OK"
            self.request.sendall(response)
            startzom()
        if data=="stop":
            response = killzom()
            self.request.sendall(response)
        if data=="check":
            response = checkzom()
            self.request.sendall(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    i = 0
    try:
        while True:
            if i==0:
                server = ThreadedTCPServer(("0.0.0.0", 16260), ThreadedTCPRequestHandler)
                ip, port = server.server_address
                server_thread = threading.Thread(target=server.serve_forever)
                server_thread.daemon = True
                server_thread.start()
                i=+1
    finally:
        server.shutdown()
        print("SHUTDOWN")

    