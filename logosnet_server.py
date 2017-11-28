import argparse
import select
import socket
import sys
import signal
import struct
import collections
import sandr

#argument parsing
PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()
PORT = ARGS.port
HOST = ARGS.ip

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
server.listen(5)

inputs = [server]
outputs = []
buf = {}
names = {}
tempNames={}

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        try:
            if s == server:
                c,addr = server.accept()
                if len(names) <= 255:
                    inputs.append(c)
                    #print("added in inputs")
                    sandr.send(c,"accepted")
                else:
                    sandr.send(c,"full")
            else:   
                if s not in outputs:
                    #inputs.remove(s)
                    #print(s)
                    #print("in S")
                    username = sandr.recv(s,tempNames)
                    if username != None:
                        print(username)
                        if len(username) > 10 or " " in username:
                            sandr.send(s,"username-invalid")
                            del tempNames[s.fileno()]
                        elif username in names.values():
                            sandr.send(s,"username-alreadyinuse")
                            del tempNames[s.fileno()]
                        else:
                            sandr.send(s,"username-valid")
                            names[s.fileno()] = username
                            del tempNames[s.fileno()]
                            outputs.append(s)
                            for output in outputs:
                                msg = "\rUser " + username + " has joined"
                                h = len(msg)
                                sandr.send(output,msg)
                    elif username == "":
                        inputs.remove(s)
                        print("about to throw excpt")
                        raise Exception("Time Out Exception")
                                       
                else:
                    byte = b''
                    messages = sandr.recv(s,buf)
                    if messages != None:
                        print(messages)
                        m = messages.split()
                        if m[0][0] == '@':
                            if len(m) == 2: 
                                targetName = m[0][1:]
                                if targetName in names.values():
                                    for o in outputs:
                                        if names[o.fileno()] == targetName:
                                            n = "\r> "+names[s.fileno()]+": "
                                            sandr.send(o,n+m[1])
                        #else broadcast
                        else:    
                            for o in outputs:
                                if o.fileno() != s.fileno():
                                    print("inside here")
                                    n = "\r> "+names[s.fileno()]+": "
                                    sandr.send(o,n+messages)
                        del buf[s.fileno()]
                    elif message = b'':
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        name = names[s.fileno()]                 
                        for output in outputs:
                            m = "\rUser " + name + " has left"
                            sandr.send(o,m+messages)                   
                        del names[s.fileno()]
                        del buf[s.fileno()]
                        s.close()

                        #print (s.fileno())
        except Exception as e:
            print("Other exception")
            print(e)

