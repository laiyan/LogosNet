'''server for the chat room'''
import argparse
import select
import socket
import sandr

#argument parsing
PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()
PORT = ARGS.port
HOST = ARGS.ip

S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.bind((HOST, PORT))
S.listen(5)

INPUTS = [S]
OUTPUTS = []
buf = {}
names = {}
tempNames = {}

while INPUTS:
    READABLE, WRITEABLE, EXCEPTIONAL = select.select(INPUTS, OUTPUTS, INPUTS)
    for s in READABLE:
        try:
            if s == S:
                c, addr = S.accept()
                if len(names) <= 255:
                    INPUTS.append(c)
                    #print("added in INPUTS")
                    sandr.send(c, "accepted")
                else:
                    sandr.send(c, "full")
            else:
                #if client is accepted but not yet being active participant
                if s not in OUTPUTS:
                    username = sandr.recv(s, tempNames)
                    if username != None:
                        if len(username) > 10 or " " in username:
                            sandr.send(s, "username-invalid")
                            del tempNames[s.fileno()]
                        elif username in names.values():
                            sandr.send(s, "username-alreadyinuse")
                            del tempNames[s.fileno()]
                        else:
                            sandr.send(s, "username-valid")
                            names[s.fileno()] = username
                            del tempNames[s.fileno()]
                            OUTPUTS.append(s)
                            for output in OUTPUTS:
                                msg = "\rUser " + username + " has joined"
                                h = len(msg)
                                sandr.send(output, msg)
                    #timeout of client exit
                    elif username == "":
                        INPUTS.remove(s)
                        print("about to throw excpt")
                        raise Exception("Time Out Exception")
                else:
                    byte = b''
                    messages = sandr.recv(s, buf)
                    #message recv
                    if messages != None:
                        #private message
                        m = messages.split()
                        if m[0][0] == '@':
                            if len(m) == 2:
                                targetName = m[0][1:]
                                if targetName in names.values():
                                    for o in OUTPUTS:
                                        if names[o.fileno()] == targetName:
                                            n = "\r> "+names[s.fileno()]+": "
                                            sandr.send(o, n+m[1])
                        #else broadcast
                        else:
                            for o in OUTPUTS:
                                if o.fileno() != s.fileno():
                                    n = "\r> "+names[s.fileno()]+": "
                                    sandr.send(o, n+messages)
                        del buf[s.fileno()]
                    elif message == b'':
                        if s in OUTPUTS:
                            OUTPUTS.remove(s)
                        INPUTS.remove(s)
                        name = names[s.fileno()]
                        for output in OUTPUTS:
                            m = "\rUser " + name + " has left"
                            sandr.send(o, m+messages)
                        del names[s.fileno()]
                        del buf[s.fileno()]
                        s.close()
        except Exception as e:
            print("Other exception")
            print(e)

