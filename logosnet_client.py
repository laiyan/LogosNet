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
buf = {}

def send(connection,message):
    header = len(message)
    connection.send(struct.pack(">i",header))
    connection.send(message.encode('utf-8'))

def recv(connection):
    buf[connection.fileno()] = connection.recv(2)
    buf[connection.fileno()] += connection.recv(2)
    if buf[connection.fileno()]:
        header = int.from_bytes(buf[connection.fileno()],byteorder='big')
        if header%2 == 1:
            header = int(header/2) + 1
        else:
            header = int (header/2)
        for i in range(0,header):
            buf[connection.fileno()] += connection.recv(2)
        print(buf[connection.fileno()].decode('utf-8')[4:])
        del buf[connection.fileno()]
                        #sys.stdout.flush()
    else:
        print("Disconnected from chat server")
        connection.close()
    

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST,PORT))
print("connect")

checklen = client.recv(4)
checklen = int.from_bytes(checklen,byteorder = 'big')
check = client.recv(checklen)
print("received")

def interrupted(signum, frame):
    connect = False
    client.close()
    print("Timeout! Bye")
    sys.exit(1)

signal.signal(signal.SIGALRM, interrupted)

if check.decode('utf-8') == 'a':
    while check.decode('utf-8') != 'v':
        signal.alarm(TIMEOUT)
        sys.stdout.write("Enter username, max 10 chars: ")
        sys.stdout.flush()
        name = sys.stdin.readline().strip()
        # disable the alarm after success
        signal.alarm(0)
        client.send(name.encode('utf-8'))
        checklen = client.recv(4)
        checklen = int.from_bytes(checklen,byteorder = 'big')
        check = client.recv(checklen)
        print(check)
    if check.decode('utf-8') == 'v':
        connect = True   
    while connect:
        try:
            sys.stdout.write("> " + name + ": ")
            sys.stdout.flush() 
            readable, writeable,exceptional = select.select([0, client], [], [])
            for s in readable:
                if s == client:
                    recv(s)
                else:            
                    data = sys.stdin.readline().strip()
                    if len(data) < 1000:
                        #client.send(struct.pack(">i",len(data)))
                        #client.send(data.encode('utf-8'))
                        send(client,data)
                        #print("sent")
                    if data == "exit()":
                        client.close()
                        break
        except KeyboardInterrupt:
            print("Client interruped. ")
            client.close()
            break
else:
    print("Chat room is full, please try again later.")
    client.close()