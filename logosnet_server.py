import argparse
import socket               # Import socket module
import os#  Low level modules for threading and handling signals
import signal
import struct
import collections
import sys
import select

class ChatServer(object):
    def __init__(self, port,host, backlog=5):
        self.clients = 0    #客户端数量
        self.clientmap = {} #客户端映射
        self.outputs = []   #输出套接字
        self.port = port
        self.host = host
        #创建TCP套接字
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #启用地址重用
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #绑定本机地址和端口号
        self.server.bind((host, port))
        #侦听客户端连接
        self.server.listen(backlog)
        #捕捉用户中断操作
        signal.signal(signal.SIGINT, self.sighandler)

    #中断信号处理方法
    def sighandler(self, signum, frame):
        #关闭所有套接字连接
        for output in self.outputs:
            output.close()
        #关闭服务器
        self.server.close()

    # def get_client_name(self, client):
    #     info = self.clientmap[client] #info的内容如：(('127.0.0.1', 56354), 'MyClient')
    #     host,name = info[0][0],info[1]
    #     return "@".join((name,host))  #返回内容如：MyClient@127.0.0.1
    def sd(c, s):
        c.send(struct.pack(">i",len(s)))
        c.send(s.encode('utf-8'))


    def run(self):
        inputs = [self.server, sys.stdin]
        self.outputs = []
        running = True
        while running:
            try:
                #开始select监听,对inputs中的服务端server、标准输入stdin进行监听
                #select函数阻塞进程，直到inputs中的套接字被触发（在此例中，套接字接收到客户端发来的握手信号，从而变得可读，满足select函数的“可读”条件），readable返回被触发的套接字（服务器套接字）
                #当再次运行此处时，select再次阻塞进程，同时监听服务器套接字和获得的客户端套接字
                readable,writeable,exceptional = select.select(inputs, self.outputs, [])
            except select.error:
                print ("Socket error")
            except Exception as e:
                print ("Other exception: %s" % str(e))
                break

            #循环判断是否有客户端连接进来,当有客户端连接进来时select将触发
            for sock in readable:
                #判断当前触发的是不是服务端对象, 当触发的对象是服务端对象时,说明有新客户端连接进来了
                #如果是服务器套接字被触发（监听到有客户端连接服务器）
                if sock == self.server:
                    client,address = self.server.accept()
                    if self.clients < 6:
                        sd(client,"a")
                        cname = client.recv(10)
                        # check duplicate
                        # if not send("v")
                        # else send("i")
                        self.clients += 1 #客户端数量加1
                        client.send("CLIENT: "+str(address[0]))
                        inputs.append(client)  #将客户端对象也加入到监听的列表中, 当客户端发送消息时 select 将触发
                        self.clientmap[client] = (address, cname) #客户端映射

                        #向其它客户端发送广播消息
                        msg = "\n(Connected: New client (%d) from %s)" % (self.clients, self.get_client_name(client))
                        for output in self.outputs:
                            output.send(msg)
                        self.outputs.append(client)
                    else:
                        client.send('f')
                    # print "Chat server: got connection %d from %s" % (client.fileno(), address)
                elif sock == sys.stdin: #如果是标准输入就发送广播消息
                    junk = sys.stdin.readline().strip()
                    if junk == "exit" or junk=="quit":
                        running = False
                    else:
                        msg = '\n#[Server]>>' + junk
                        for output in self.outputs:
                            if output != sock:
                                output.send(msg)

                else: #由于客户端连接进来时服务端接收客户端连接请求，将客户端加入到了监听列表中(inputs)，客户端发送消息将触发，所以判断是否是客户端对象触发
                    try:
                        data = sock.recv(1024)
                        if data:
                            #向其它客户端发送广播消息
                            msg = '\n#[' + self.get_client_name(sock) + ']>>' + data
                            for output in self.outputs:
                                if output != sock:
                                    output.send(msg)
                        else:
                            #客户端退出，断开连接
                            print ("Chat server: %d hung up" % sock.fileno())
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock) #客户端断开连接了，将客户端的监听从inputs列表中移
                            self.outputs.remove(sock)
                            #发送广播消息告知其它客户端
                            msg = "\n(Now hung up: Client from %s)" % self.get_client_name(sock)
                            for output in self.outputs:
                                output.send(msg)
                    except socket.error:
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        print ("Socket error")
                    except Exception as e:
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        print ("Other exception: %s" % str(e))

        self.server.close()
#argument parsing
PARSER = argparse.ArgumentParser(
    description='LogosNet Server, the server version for the primitive networked chat program')
PARSER.add_argument("--port", type=int, metavar='p', help="port number")
PARSER.add_argument("--ip", metavar='i', help="IP address for client")
ARGS = PARSER.parse_args()
PORT = ARGS.port
HOST = ARGS.ip
server = ChatServer(PORT, HOST)
server.run()
