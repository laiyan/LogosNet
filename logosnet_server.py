import argparse
import socket               # Import socket module
import signal
import struct
import collections
import threading

def broadcast_data (sock, message):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)

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


# server socket setup and connection
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
HOST = ARGS.ip
PORT = ARGS.port               # Reserve a PORT for your service.
S.bind((HOST, PORT))
S.listen(5)                 # Now wait for client connection.
print('Server', socket.gethostbyname('localhost'), 'listening ...')

mydict = dict()
mylist = list()

#把whatToSay传给除了exceptNum的所有人
def tellOthers(exceptNum, whatToSay):
    for c in mylist:
        if c.fileno() != exceptNum :
            try:
                c.send(whatToSay.encode())
            except:
                pass

def subThreadIn(myconnection, connNumber):
    nickname = myconnection.recv(1024).decode()
    mydict[myconnection.fileno()] = nickname
    mylist.append(myconnection)
    print('connection', connNumber, ' has nickname :', nickname)
    tellOthers(connNumber, '【'+mydict[connNumber]+' enter chatroom】')
    while True:
        try:
            recvedMsg = myconnection.recv(1024).decode()
            if recvedMsg:
                print(mydict[connNumber], ':', recvedMsg)
                tellOthers(connNumber, mydict[connNumber]+' :'+recvedMsg)

        except (OSError, ConnectionResetError):
            try:
                mylist.remove(myconnection)
            except:
                pass
            print(mydict[connNumber], 'exit, ', len(mylist), ' person left')
            tellOthers(connNumber, '【'+mydict[connNumber]+' left chatroom】')
            myconnection.close()
            return

while True:
    connection, addr = S.accept()
    print('Accept a new connection', connection.getsockname(), connection.fileno())
    try:
        #connection.settimeout(5)
        buf = connection.recv(1024).decode()
        if buf == '1':
            connection.send(b'welcome to server!')

            #为当前连接开辟一个新的线程
            mythread = threading.Thread(target=subThreadIn, args=(connection, connection.fileno()))
            mythread.setDaemon(True)
            mythread.start()

        else:
            connection.send(b'please go out!')
            connection.close()
    except :
        pass
