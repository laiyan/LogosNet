import socket
import struct

def recv(conn, buf):
    temp = conn.recv(2)
    if conn.fileno() not in buf.keys():
        buf[conn.fileno()] = temp
        return None
    else:
        tempLen = len(buf[conn.fileno()])
        if tempLen > 4 or (tempLen ==4 and int.from_bytes(buf[conn.fileno()],byteorder = 'big') < 3):
            tempTup = struct.unpack(">i " + str(tempLen-4) +"s", buf[conn.fileno()])
            if tempLen != tempTup[0]+4:
                buf[conn.fileno()] += temp
                if len(buf[conn.fileno()])-4 == tempTup[0]:
                    message = str(tempTup[1]+temp,'utf-8')
                    buf[conn.fileno()] = ""
                    return message
                else:
                    return None
        else:
            buf[conn.fileno()] += temp
            return None

def send(connection,message):
    header = len(message)
    connection.send(struct.pack(">i",header))
    connection.send(message.encode('utf-8'))

