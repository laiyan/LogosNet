import argparse
import select
import socket
import sys

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
            else:
                #active participant
                #data = s.recv()