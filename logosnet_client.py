'''client for chatroom'''
import argparse
import select
import socket
import sys
import signal
import struct

PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()
PORT = ARGS.port
HOST = ARGS.ip

TIMEOUT = 60
BUF = {}

def send(connection, message):
    '''send function'''
    header = len(message)
    connection.send(struct.pack(">i", header))
    connection.send(message.encode('utf-8'))

def recv(connection):
    '''recv function, recv by 2 bytes'''
    BUF[connection.fileno()] = connection.recv(2)
    BUF[connection.fileno()] += connection.recv(2)
    if BUF[connection.fileno()]:
        header = int.from_bytes(BUF[connection.fileno()], byteorder='big')
        if header%2 == 1:
            header = int(header/2) + 1
        else:
            header = int(header/2)
        for i in range(0, header):
            BUF[connection.fileno()] += connection.recv(2)
        print(BUF[connection.fileno()].decode('utf-8')[4:])
        del BUF[connection.fileno()]
    else:
        print("Disconnected from chat server")
        connection.close()

C = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
C.connect((HOST, PORT))
#print("connect")

CHECKLEN = C.recv(4)
CHECKLEN = int.from_bytes(CHECKLEN, byteorder='big')
CHECK = C.recv(CHECKLEN)
#print("received")

def interrupted(signum, frame):
    '''If exceed 60s'''
    #C.close()
    print("Time out!")
    raise Exception("Time Out Exception")
    #sys.exit(1)

signal.signal(signal.SIGALRM, interrupted)


if CHECK.decode('utf-8') == 'a':
    while CHECK.decode('utf-8') != 'v':
        try:
            signal.alarm(TIMEOUT)
            sys.stdout.write("Enter username, max 10 chars: ")
            sys.stdout.flush()
            name = sys.stdin.readline().strip()
            # disable the alarm after success
            signal.alarm(0)
            #print("sending in username")
            C.send(name.encode('utf-8'))
            CHECKLEN = C.recv(4)
            CHECKLEN = int.from_bytes(CHECKLEN, byteorder='big')
            CHECK = C.recv(CHECKLEN)
            #print(CHECK)
        except KeyboardInterrupt:
            print("C interruped. ")
            C.close()
            CONNECT = False
            break
        except Exception:
            print("Other exception")
            C.close()
            CONNECT = False
            break
    if CHECK.decode('utf-8') == 'v':
        CONNECT = True
    while CONNECT:
        try:
            sys.stdout.write("> " + name + ": ")
            sys.stdout.flush()
            R, W, E = select.select([0, C], [], [])
            for s in R:
                if s == C:
                    recv(s)
                else:
                    data = sys.stdin.readline().strip()
                    if len(data) < 1000:
                        send(C, data)
                    if data == "exit()":
                        C.close()
                        break
        except KeyboardInterrupt:
            print("C interruped. ")
            C.close()
            break
else:
    print("Chat room is full, please try again later.")
    C.close()