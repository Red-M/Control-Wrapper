#!/usr/bin/env python
import subprocess
import sys
import time
import socket
import threading
import SocketServer

global process_exec
process_exec = "/path/to/executable/here"
global greprexp
greprexp = 'ps aux | grep "java -D"'

# edit the varibles above for the process path you are trying to run and 
# the grep command will need to be edited to match the process you are looking for
# just replace the "java -D" section with what will match for your process

global startzom
def startzom():
    global proc
    isonline = checkzom()
    if isonline=="OFF-LINE":
        if proc==None:
            proc = subprocess.Popen(process_exec.split(" "))
            print("STARTED")
            try:
                while proc.wait():
                    #return("DONE")
                    pass
            except Exception,e:
                pass
        
global killzom
def killzom():
    global proc
    isonline = checkzom()
    if isonline=="ON-LINE":
        if not proc==None:
            proc.kill()
            print("KILLED")
            proc = None
            return("KILLED")
    else:
        return("NO SERVER")
    
global checkzom
def checkzom():
    if proc==None:
        return("OFF-LINE")
    else:
        return("ON-LINE")
    return("None")
    
    
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
        if data=="restart":
            killzom()
            response = "OK"
            self.request.sendall(response)
            startzom()
        if data=="check":
            response = checkzom()
            self.request.sendall(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    i = 0
    proc = None
    server = None
    try:
        while True:
            if i==0:
                server = ThreadedTCPServer(("0.0.0.0", 16260), ThreadedTCPRequestHandler)
                ip, port = server.server_address
                server_thread = threading.Thread(target=server.serve_forever)
                server_thread.daemon = True
                server_thread.start()
                print("Started the process daemon.")
                i=+1
    except Exception,e:
        if not proc==None:
            proc.kill()
        if not server==None:
            server.shutdown()
            print("SHUTDOWN")
        else:
            print("Failed to start.\n"+str(e))

    