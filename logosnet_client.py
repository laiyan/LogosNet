import argparse
import socket               # Import socket module
import signal
import struct
import threading

#username method
def get_username():
    '''for inputing the username and check duplicate'''
    inputName = input("Enter username, max 10 chars: ")
    while len(inputName) > 10 or " " in inputName:
        inputName = input("Enter username, max 10 chars: ")
    print(inputName)
    return inputName

#argument parsing
PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()

S = socket.socket()         # Create a socket object
HOST = ARGS.ip            # Get local machine name
PORT = ARGS.port              # Reserve a PORT for your service.

S.connect((HOST, PORT))
S.send(b'1')
print(S.recv(1024).decode())
nickName = input('input your nickname: ')
S.send(nickName.encode())
#S.close                     # Close the socket when done
