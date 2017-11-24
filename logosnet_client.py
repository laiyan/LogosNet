import argparse
import socket               # Import socket module
import signal
import struct
import time

#username method
def get_username():
    '''for inputing the username and check duplicate'''
    inputName = input("Enter username, max 10 chars: ")
    while len(inputName) > 10 or " " in inputName:
        inputName = input("Enter username, max 10 chars: ")
    print(inputName)
    return inputName

#argument parsing


class ChatClient(object):
    def __init__(self, port, host):
        self.name = " " #客户端名称
        self.connected = False
        self.host = host
        self.port = port
        # 初始化提示
        #self.prompt = "[" + "@".join((name, socket.gethostname().split(".")[0])) + ']> '
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            self.connected = True
            #self.sock.send("NAME: " + self.name) #向服务端发送本客户端名称
            data = self.sock.recv(1)
            #addr = data.split('CLIENT: ')[1] # 客户端IP地址
            #self.prompt = '[' + '@'.join((self.name, addr)) + ']> '
            if data == 'a':
                check = 'i'
                start = time.time()         #the variable that holds the starting time
                elapsed = 0                 #the variable that holds the number of seconds elapsed.
                while (len(self.name)>10 or " "in self.name) and elapsed < 60 and check == 'i':
                    self.prompt = "Enter username, max 10 chars: "
                    self.name = sys.stdin.readline().strip()
                    elapsed =time.time - start
                    if elapsed > 60:
                        self.prompt = "Timeout, didn't input username in 60s"
                        self.sock.close()
                         break
                    else:
                        self.sock.send(self.name)
                        check = self.sock.recv(1)
                self.prompt = "User "+ self.name + " has joined."
            else:
                self.prompt = "Chat server is full, try later"
                self.sock.close()

        except socket.error:
            print ("Failed to connect to chat server")
            sys.exit(1)
        except Exception as e:
            print ("Other exception: %s" % str(e))
            sys.exit(1)

    def run(self):
        while self.connected:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
                #开始select监听,对标准输入stdin和客户端套接字进行监听
                #注意：Windows 版本的 Python, select() 函数只能接受 socket, 不接受 File Object, 所以不能 select 标准输入输出.
                readable, writeable,exceptional = select.select([0, self.sock], [], [])
                for sock in readable:
                    if sock == 0:
                        data = sys.stdin.readline().strip() #获取控制台输入，并移除字符串头尾空格字符
                        if data:
                            self.sock.send(data)
                    elif sock == self.sock:
                        data = self.sock.recv(1024)
                        if not data:
                            print 'Client shutting down.'
                            self.connected = False
                            break
                        else:
                            sys.stdout.write(data + '\n')
                            sys.stdout.flush()
            except KeyboardInterrupt:
                print " Client interrupted. """
                self.sock.close()
                break
            except Exception as e:
                print "Other exception: %s" % str(e)
                self.sock.close()
                break


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description='LogosNet Server, the server version for the primitive networked chat program')
    PARSER.add_argument("--port", type=int, metavar='p', help="port number")
    PARSER.add_argument("--ip", metavar='i', help="IP address for client")
    ARGS = PARSER.parse_args()
    PORT = ARGS.port
    HOST = ARGS.ip
    client = ChatClient(PORT,HOST)
    client.run()
