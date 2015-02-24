#!/usr/bin/env python
import subprocess
import sys
import time
import socket
import threading
import SocketServer
import traceback

process_exec = "/path/to/executable/here"

class process_control(object):

    def __init__(self,process_exec):
        self.proc = None
        self.process_exec = process_exec
    
    def startzom(self):
        isonline = self.checkzom()
        if isonline=="OFF-LINE":
            if self.proc==None:
                self.proc = subprocess.Popen(self.process_exec.split(" "))
                print("STARTED")
                try:
                    while self.proc.wait():
                        #return("DONE")
                        pass
                except Exception,e:
                    pass
    
    
    def killzom(self):
        isonline = self.checkzom()
        if isonline=="ON-LINE":
            if not self.proc==None:
                self.proc.kill()
                print("KILLED")
                self.proc = None
                return("KILLED")
        else:
            return("NO SERVER")
    
    
    def checkzom(self):
        if self.proc==None:
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
            self.server.child_process.startzom()
        if data=="stop":
            response = self.server.child_process.killzom()
            self.request.sendall(response)
        if data=="restart":
            self.server.child_process.killzom()
            response = "OK"
            self.request.sendall(response)
            self.server.child_process.startzom()
        if data=="check":
            response = self.server.child_process.checkzom()
            self.request.sendall(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, child_process, *args, **kwargs):
        self.child_process = child_process
        SocketServer.TCPServer.__init__(self, *args, **kwargs)


def main(process_exec):
    i = 0
    proc = None
    server = None
    try:
        while True:
            if i==0:
                child_process = process_control(process_exec)
                server = ThreadedTCPServer(child_process, ("0.0.0.0", 16260), ThreadedTCPRequestHandler)
                ip, port = server.server_address
                server_thread = threading.Thread(target=server.serve_forever)
                server_thread.daemon = True
                server_thread.start()
                print("Started the process daemon.")
                i=+1
    except Exception,e:
        type_, value_, traceback_ = sys.exc_info()
        ex = traceback.format_exception(type_, value_, traceback_)
        trace = ""
        for data in ex:
            trace = str(trace+data)
        if not proc==None:
            proc.kill()
        if not server==None:
            server.shutdown()
            print("SHUTDOWN")
        else:
            print("Failed to start.\n"+str(trace))

main(process_exec)