'''client for chatroom'''
import argparse
import select
import socket
import sys
import signal
import struct
import sandr
PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()
PORT = ARGS.port
HOST = ARGS.ip

TIMEOUT = 60
BUF = {}

def recv(connection):
    '''recv function, recv by 2 bytes'''
    msg = connection.recv(2)
    msg += connection.recv(2)
    if msg:
        header = int.from_bytes(msg, byteorder='big')
        if header%2 == 1:
            header = int(header/2) + 1
        else:
            header = int(header/2)
        for i in range(0, header):
            msg += connection.recv(2)
    return msg

C = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
C.connect((HOST, PORT))

CHECK = recv(C)
CHECK = CHECK[4:]


def interrupted(signum, frame):
    '''If exceed 60s'''
    print("Time out!")
    raise Exception("Time Out Exception")

signal.signal(signal.SIGALRM, interrupted)


if CHECK.decode('utf-8') == "accepted":
    while CHECK.decode('utf-8') != "username-valid":
        try:
            signal.alarm(TIMEOUT)
            sys.stdout.write("Enter username, max 10 chars: ")
            sys.stdout.flush()
            if CHECK.decode('utf-8') == "username-alreadyinuse":
                print("\ralready in use")
                signal.alarm(TIMEOUT)
            NAME = sys.stdin.readline().strip()
            signal.alarm(0)
            # disable the alarm after success
            print(struct.pack(">i " + str(len(NAME))+"s", len(NAME), bytes(NAME, 'utf-8'))
            sandr.send(C, NAME)
            CHECK = recv(C)
            CHECK = CHECK[4:]
            #print(CHECK)
        except KeyboardInterrupt:
            print("C interruped. ")
            C.close()
            CONNECT = False
            break
        except Exception as e:
            print("Other exception")
            print(str(e))
            C.close()
            CONNECT = False
            break
    if CHECK.decode('utf-8') == "username-valid":
        CONNECT = True
    while CONNECT:
        try:
            sys.stdout.write("> " + name + ": ")
            sys.stdout.flush()
            R, W, E = select.select([0, C], [], [])
            for s in R:
                if s == C:
                    data = recv(s)
                    if data:
                        print(data.decode('utf-8')[4:])
                        del data
                    else:
                        print("Disconnected from chat server")
                        s.close()
                else:
                    data = sys.stdin.readline().strip()
                    if len(data) < 1000:
                        sandr.send(C, data)
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
    