import argparse
import select
import socket
import sys
import signal
import struct

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

    #中断信号处理方法
def sighandler(signum, frame):
    for output in outputs:
        output.close()
    server.close()

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        if s == server:
            c,addr = server.accept()
            if clients < 3:
                inputs.append(c)
                print("added in inputs")
                c.send('a'.encode('utf-8'))
                clients = clients + 1
                buf[s.fileno()] = ""
            else:
                c.send('f'.encode('utf-8'))
        else:
            if s not in outputs:
                username = s.recv(16).decode('utf-8')
                print("received username")
                if len(username) > 10 or " " in username:
                    s.send('i'.encode('utf-8'))
                else:
                    s.send('v'.encode('utf-8'))
                    clients = clients + 1
                    outputs.append(s)
                    for output in outputs:
                        if output != s:
                            output.send(("User " + username+ " has joined").encode('utf-8'))
                    
            else:
                #active participant
                data = s.recv(2)
                if len(buf[s.fileno()]) > 4 bytes
                    header = 
                    struct.pack(">i",header)
                         if(buf[s.fileno()].len - 4 = value in header)
                                send the friggin message
                                del 
                         
                else
                       
                