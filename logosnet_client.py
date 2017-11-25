import argparse
import select
import socket
import sys
import signal

PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()
PORT = ARGS.port
HOST = ARGS.ip

TIMEOUT = 60

client = socket.socket()
client.connect((HOST,PORT))
print("connect")

check = client.recv(4)
print("received")

def interrupted(signum, frame):
    print("Timeout! Bye")
    client.close()
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
        check = client.recv(4)
        print(check)
    if check.decode('utf-8') == 'v':
        connect = True    
    while connect:
        try:
            sys.stdout.write(">" + name + ": ")
            sys.stdout.flush()
            readable, writeable,exceptional = select.select([0, client], [], [])
            for s in readable:
                if s == client:
                    data = s.recv(1024)
                    print(data.decode('utf-8'))
                else:            
                    sys.stdout.write(">" + name + ": ")
                    sys.stdout.flush()
                    data = sys.stdin.readline().strip()
                    if len(data) < 1000:
                        client.send(data.encode('utf-8'))
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