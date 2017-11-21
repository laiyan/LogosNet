import argparse
import socket               # Import socket module
import signal
import struct

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
#S.close                     # Close the socket when done
