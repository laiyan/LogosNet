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

def sendThreadFunc():
    while True:
        try:
            myword = input()
            S.send(myword.encode())
            #print(sock.recv(1024).decode())
        except ConnectionAbortedError:
            print('Server closed this connection!')
        except ConnectionResetError:
            print('Server is closed!')

def recvThreadFunc():
    while True:
        try:
            otherword = S.recv(1024)
            if otherword:
                print(otherword.decode())
            else:
                pass
        except ConnectionAbortedError:
            print('Server closed this connection!')

        except ConnectionResetError:
            print('Server is closed!')


th1 = threading.Thread(target=sendThreadFunc)
th2 = threading.Thread(target=recvThreadFunc)
threads = [th1, th2]

for t in threads :
    t.setDaemon(True)
    t.start()
t.join()

#S.close                     # Close the socket when done
