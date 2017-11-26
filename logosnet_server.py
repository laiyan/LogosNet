import argparse
import select
import socket
import sys
import signal
import struct
import collections

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
clients = 0
buf = {}
names = {}

def sighandler(signum, frame):
    for output in outputs:
        output.close()
    server.close()

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        if s == server:
            c,addr = server.accept()
            if clients < 5:
                inputs.append(c)
                print("added in inputs")
                c.send('a'.encode('utf-8'))
                clients = clients + 1
                #print(buf[s.fileno()])
            else:
                c.send('f'.encode('utf-8'))
        else:   
            if s not in outputs:
                username = s.recv(16).decode('utf-8')
                print("received username")
                if len(username) > 10 or " " in username or username in names.values():
                    s.send('i'.encode('utf-8'))
                else:
                    s.send('v'.encode('utf-8'))
                    clients = clients + 1
                    names[s.fileno()] = username
                    outputs.append(s)
                    for output in outputs:
                        if output != s:
                            msg = "\rUser " + username+ " has joined"
                            #output.send(struct.pack(">i",len(msg)))
                            h = len(msg)
                            output.send(struct.pack(">i",h)+(msg.encode('utf-8')))                   
            else:
                #This part is for clients already added to outputs
                #active participant
                #h = struct.unpack('>i',data)
                #print(h)
                print(buf.keys())
                #if s.fileno() not in buf.keys():
                buf[s.fileno()] = s.recv(2)
                buf[s.fileno()] += s.recv(2)
                if buf[s.fileno()]:
                    header = struct.unpack('>i',buf[s.fileno()])[0]                    
                    #print (header)
                    fmt = ">I " + str(header) + "s"
                    if header%2 == 1:
                        header = int(header/2) + 1
                    else:
                        header = int (header/2)
                    for i in range(0,header):
                        buf[s.fileno()] += s.recv(2)
                                       
                    temp = struct.unpack(fmt, buf[s.fileno()])
                    #print (temp)
                    #if private message do this
                    messages = str(temp[1], 'utf-8').split()
                    #print("yes: "+messages[0])
                    #print("yes yes: "+ messages[0][0])
                    if(messages[0][0] == '@'):
                        if len(messages) == 2: 
                            targetName = messages[0][1:]
                            if targetName in names.values():
                                for o in outputs:
                                    if names[o.fileno()] == targetName:
                                        n = "\r> "+names[s.fileno()]+": "
                                        h = temp[0] + len (n)
                                        #print("yeah" + str(h))                                       
                                        #print( type(n))
                                        #print(type(messages[1]))
                                        o.send(struct.pack(">i "+ str(h) + "s",h,bytes(n+messages[1], 'utf-8')))
                    #else broadcast
                    else:    
                        for o in outputs:
                            if o.fileno() != s.fileno():
                                print(struct.pack(">i",len(buf[s.fileno()])-4))
                                #o.send(struct.pack(">i",len(buf[s.fileno()])-4))
                                n = "\r> "+names[s.fileno()]+": "
                                h = len(buf[s.fileno()])-4 + len(n)
                                #print(type(buf[s.fileno()]))
                                m = buf[s.fileno()].decode('utf-8')[4:]
                                o.send(struct.pack(">i",h) + n.encode('utf-8') + m.encode('utf-8'))
                    del buf[s.fileno()]
                    #break
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    del names[s.fileno()]
                    del buf[s.fileno()]
                    clients = clients - 1
                    s.close()
                    print (s.fileno())
                    
                #    if len(buf[s.fileno()]) - 4 == header:
                 #       print(buf[s.fileno()])
                  #      for o in outputs:
                   #         if output != s:
                    #            o.send(buf[s.fileno()])
                     #   del bufbuf[s.fileno()]
                   # else:
                    #    buf[s.fileno()]+= s.recv(2)