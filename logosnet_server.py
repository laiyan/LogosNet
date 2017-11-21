import argparse
import socket               # Import socket module
import signal
import struct
import collections

#object Participant
class Participant(object):
    def __init__(self, socketfd,username,message):
        self.socketfd = socketfd
        self.username = username
        self.message = message

participants = []

for i in range(0, 255):
    participants.append(Participant(-1," "," "))

#argument parsing
PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()

#check duplicate usernam
def checkDuplicate():
    '''check username has been used or not'''
    for i in range (0,255):
        if participants[i].username == inputName:
            return 0
        else:
            return 1
    return 1

#username method
def get_username():
    '''for inputing the username and check duplicate'''
    inputName = input("Enter username, max 10 chars: ")
    while len(inputName) > 10 or " " in inputName:
        inputName = input("Enter username, max 10 chars: ")
    print(inputName)
    return inputName

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
