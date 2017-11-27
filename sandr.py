import socket
import struct

def recv(connection):
    return connection.recv(2)

def send(connection,message):
    header = len(message)
    connection.send(struct.pack(">i",header))
    connection.send(message.encode('utf-8'))