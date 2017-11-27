import argparse
import select
import socket
import sys
import signal
import struct
import collections
import sandr

#argument parsing
PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()
PORT = ARGS.port
HOST = ARGS.ip

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
server.listen(5)

inputs = [server]
outputs = []
buf = {}
names = {}
tempNames={}

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        try:
            if s == server:
                c,addr = server.accept()
                if len(names) <= 255:
                    inputs.append(c)
                    #print("added in inputs")
                    sandr.send(c,"accepted")
                else:
                    sandr.send(c,"full")
            else:
                if s not in outputs:
                    #inputs.remove(s)
                    #print(s)
                    print("in S")
                    if s.fileno() in tempNames.keys():
                        tempLength = len(tempNames[s.fileno()])
                        print(tempLength)
                        if tempLength > 4 or (tempLength == 4 and int.from_bytes(tempNames[s.fileno()],byteorder='big') < 3):
                            tempTup = struct.unpack(">i " + str(tempLength-4) +"s", tempNames[s.fileno()])
                            print("Printing Tuple")
                            print(tempTup[0])
                            if tempLength != tempTup[0]:
                                temp = sandr.recv(s)
                                print("in deep if")
                                print(temp)
                                tempNames[s.fileno()] += temp
                                if len(tempNames[s.fileno()])-4 == tempTup[0]:
                                    print("in here bla")
                                    username = str(tempTup[1]+temp,'utf-8')
                                    if len(username) > 10 or " " in username:
                                        sandr.send(s,"username-invalid")
                                        del tempNames[s.fileno()]
                                    elif username in names.values():
                                        sandr.send(s,"username-alreadyinuse")
                                        del tempNames[s.fileno()]
                                    else:
                                        sandr.send(s,"username-valid")
                                        #print("sent valid")
                                        names[s.fileno()] = username
                                        del tempNames[s.fileno()]
                                        #inputs.append(s)
                                        outputs.append(s)
                                    for output in outputs:
                                        msg = "\rUser " + username + " has joined"
                                        #output.send(struct.pack(">i",len(msg)))
                                        h = len(msg)
                                        output.send(struct.pack(">i",h)+(msg.encode('utf-8')))
                        else:
                            print("in here")
                            temp = sandr.recv(s)
                            print(temp)
                            tempNames[s.fileno()] += temp
                    else:
                        temp = sandr.recv(s)
                        print("In temp")
                        print(temp)
                        if len(temp) > 0:
                            tempNames[s.fileno()] = temp
                        else:
                            inputs.remove(s)
                            print("about to throw excpt")
                            raise Exception("Time Out Exception")

                else:
                    #print(buf.keys())
                    buf[s.fileno()] = s.recv(2)
                    buf[s.fileno()] += s.recv(2)
                    if buf[s.fileno()]:
                        header = struct.unpack('>i',buf[s.fileno()])[0]
                        #print (header)
                        fmt = ">I " + str(header) + "s"
                        if header%2 == 1:
                            header = int(header/2) + 1
                        else:
                            header = int (header/2)
                        for i in range(0,header):
                            buf[s.fileno()] += s.recv(2)

                        temp = struct.unpack(fmt, buf[s.fileno()])
                        #print (temp)
                        #if private message do this
                        messages = str(temp[1], 'utf-8').split()
                        #print("yes: "+messages[0])
                        #print("yes yes: "+ messages[0][0])
                        if(messages[0][0] == '@'):
                            if len(messages) == 2:
                                targetName = messages[0][1:]
                                if targetName in names.values():
                                    for o in outputs:
                                        if names[o.fileno()] == targetName:
                                            n = "\r> "+names[s.fileno()]+": "
                                            h = temp[0] + len (n)
                                            #print("yeah" + str(h))
                                            #print( type(n))
                                            #print(type(messages[1]))
                                            o.send(struct.pack(">i "+ str(h) + "s",h,bytes(n+messages[1], 'utf-8')))
                        #else broadcast
                        else:
                            for o in outputs:
                                if o.fileno() != s.fileno():
                                    #print(struct.pack(">i",len(buf[s.fileno()])-4))
                                    #o.send(struct.pack(">i",len(buf[s.fileno()])-4))
                                    n = "\r> "+names[s.fileno()]+": "
                                    h = len(buf[s.fileno()])-4 + len(n)
                                    #print(type(buf[s.fileno()]))
                                    m = buf[s.fileno()].decode('utf-8')[4:]
                                    o.send(struct.pack(">i",h) + n.encode('utf-8') + m.encode('utf-8'))
                        del buf[s.fileno()]
                    else:
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        name = names[s.fileno()]
                        for output in outputs:
                            msg = "\rUser " + name + " has left"
                                #output.send(struct.pack(">i",len(msg)))
                            h = len(msg)
                            output.send(struct.pack(">i",h)+(msg.encode('utf-8')))
                        del names[s.fileno()]
                        del buf[s.fileno()]
                        s.close()
                        #print (s.fileno())
        except Exception as e:
            print("Other exception")
            print(e)
