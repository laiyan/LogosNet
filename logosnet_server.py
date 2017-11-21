import argparse
import socket               # Import socket module
import os#  Low level modules for threading and handling signals
import signal
import struct
import collections

#object Participant
class Participant:
    n = 0
    usernane = " "
    message = " "



#argument parsing
PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()

def chat():
    plist = collections.deque(maxlen = 255)
    get_username()

#username method
def get_username():
    '''for inputing the username.'''
    inputusername = input("Enter username, max 10 chars: ")
    while len(inputusername) > 10 or " " in inputusername:
        inputusername = input("Enter username, max 10 chars: ")
    print(inputusername)
    return inputusername

#check username exist or not



# server socket setup and connection
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
HOST = ARGS.ip
PORT = ARGS.port               # Reserve a PORT for your service.
S.bind((HOST, PORT))
S.listen(5)                 # Now wait for client connection.
while True:
    get_username()
    C, ADDR = S.accept()     # Establish connection with client. This where server waits
    C.close()                # Close the connection
S.close()
