#!/usr/bin/env python
import subprocess
import sys
import os
import time
import inspect
import json
import socket
import threading
import SocketServer
import traceback
import hashlib

os.chdir('.' or sys.path[0])
global current_dir
folders = sys.argv[0].split(os.sep)
proper_path = os.sep.join(folders[0:-1])
current_dir = os.path.join(os.getcwd(),proper_path)
if current_dir.endswith("."):
    current_dir = current_dir[0:-1]

class ProcessControl(object):

    def __init__(self,process_exec):
        self.proc = None
        self.process_exec = process_exec
    
    def start(self):
        isonline = self.check()
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
    
    
    def kill(self):
        isonline = self.check()
        if isonline=="ON-LINE":
            if not self.proc==None:
                self.proc.kill()
                print("KILLED")
                self.proc = None
                return("KILLED")
        else:
            return("NO SERVER")
    
    
    def check(self):
        if self.proc==None:
            return("OFF-LINE")
        else:
            return("ON-LINE")
        return("None")
    
    
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        conf = config(os.path.join(current_dir,"config"))
        for data in conf["processes"]:
            self.server.child_process[data]["password"] = conf["processes"][data]["password"]
        data = self.request.recv(1024)
        protodata = data.split(",")
        proc = protodata[0]
        user = protodata[1]
        hpass = protodata[2]
        action = protodata[3]
        password = hash(self.server.child_process[proc]["password"]+str(time.time())[0:9]+action)
        if user == conf["username"] and hpass == password:
            if action=="start":
                response = "OK"
                self.request.sendall(response)
                self.server.child_process[proc]["process"].start()
            if action=="stop":
                response = self.server.child_process[proc]["process"].kill()
                self.request.sendall(response)
            if action=="restart":
                self.server.child_process[proc]["process"].kill()
                response = "OK"
                self.request.sendall(response)
                self.server.child_process[proc]["process"].start()
            if action=="check":
                response = self.server.child_process[proc]["process"].check()
                self.request.sendall(response)
        else:
            print("bad user/pass")

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, child_process, *args, **kwargs):
        self.child_process = child_process
        SocketServer.TCPServer.__init__(self, *args, **kwargs)

def config_init(configlocation):
    if not os.path.exists(configlocation):
        open(configlocation, 'w').write(inspect.cleandoc(
        r'''{
         "processes": {
           "1": {
             "process": "/command/to/exe",
             "password": "password"
           }
         },
         "username": "user",
         "port": 16260
        }''') + '\n')
        
def config(configlocation):
    try:
        con = json.load(open(configlocation))
        return(con)
    except ValueError, e:
        print 'ERROR: malformed config!', e
        
def hash(input):
    return(hashlib.sha256(input).hexdigest())

def main():
    i = 0
    proc = None
    server = None
    conflocation = os.path.join(current_dir,"config")
    config_init(conflocation)
    global conf
    conf = config(conflocation)
    child_process = {}
    for data in conf["processes"]:
        child_process[data] = {}
        child_process[data]["process"] = ProcessControl(conf["processes"][data]["process"])
        child_process[data]["password"] = conf["processes"][data]["password"]
    try:
        while True:
            if i==0:
                SocketServer.ThreadingTCPServer.allow_reuse_address = True
                server = ThreadedTCPServer(child_process, ("0.0.0.0", conf["port"]), ThreadedTCPRequestHandler)
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

main()

#TODO:
#config file
#multiplexing