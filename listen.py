import sys
import getopt
import hashlib
import random
import socket


from init import *
from socketserver import BaseRequestHandler, ThreadingTCPServer


userInfo = []


class Handler(BaseRequestHandler):
    # 我觉得似乎是你需要异步I/O
    def handle(self):
        address, pid = self.client_address
        print('# %s connected!\n' % address)
        # CHAP
        receiveCHAPSalt = self.request.recv(BUF_SIZE).decode('utf-8')
        print('# CHAP Challenge message received')

        originMsg = resolve(receiveCHAPSalt)
        receiveUUID = originMsg[1][:36]
        receiveUsername = originMsg[1][36:]
        flag = 0
        for i in userInfo:
            if i['username'] == receiveUsername:
                tempPswd = i['password']
                flag = 1
                break
        if flag == 0:
            print(noSuchUserErrorMsg)
            self.request.sendall(noSuchUserErrorMsg.encode('utf-8'))
        else:
            rawHash = genearteMD5(receiveUUID + tempPswd)
            chap2 = chap_hash(len(receiveUsername), receiveUsername, len(rawHash), rawHash)
            self.request.sendall(chap2.tostring().encode('utf-8'))
            print('# CHAP Hash message sent')
            receiveCHAPResult = resolve(self.request.recv(BUF_SIZE).decode('utf-8'))[1]
            if receiveCHAPResult != "True":
                print(hashFailedErrorMsg)
            else:
                print(hashSuccessMsg)
                bind1 = resolve(self.request.recv(BUF_SIZE).decode('utf-8'))
                lisPort = int(bind1[2])
                if lisPort == 0:
                    lisPort = random.randint(10000, 65535)  # +端口检测
                print("# Bind Request No.%s message received\n# Ready to listen Port: " % bind1[1] + str(lisPort))
                res = True
                try:
                    sk = socket.socket()
                    sk.bind(("127.0.0.1", lisPort))
                    sk.listen(5)
                    print("# Able to listen Port: " + str(lisPort))
                    # conn, address = sk.accept()
                except Exception:
                    print("# Unable to listen Port: " + str(lisPort))
                    res = False               
                bind2 = bind_response(bind1[1], res, lisPort)
                self.request.sendall(bind2.tostring().encode('utf-8'))
                print("# Bind Response No.%s message sent\n" % bind1[1])
                if res:
                    print('# Waiting for connection request...\n')
                    ###

                    conn, address = sk.accept()

                    ###
                    conn1 = connect_request(random.randint(10000, 99999), bind1[2])
                    self.request.sendall(conn1.tostring().encode('utf-8'))
                    print('# Connection Request No. %d sent' % conn1.requestID)
                    recvConn2 = resolve(self.request.recv(BUF_SIZE).decode('utf-8'))
                    print('# Connection Response No. %d received' % conn1.requestID)
                    if recvConn2[2] == 'False':
                        print("# Error: Unable to connect")
                    else:
                        print('\n# IMPORTANT # Data tranfer begin\n# CONNECTION_ID = %s\n' % recvConn2[3])
                        ###

                        CONNID = recvConn2[3]

                        # data trans
                        i = 1
                        while i <= TIMES:
                            _data = conn.recv(BUF_SIZE).decode('utf-8')
                            toSlave = data(CONNID, 0, _data)
                            self.request.sendall(toSlave.tostring().encode('utf-8'))
                            print('# CONNECTION ID: %s # "%s" reposted!' % (CONNID, _data))
                            i = i + 1

                        i = 1
                        while i <= TIMES:
                            recvData = resolve(self.request.recv(BUF_SIZE).decode('utf-8'))
                            content = recvData[2]
                            conn.sendall(content.encode('utf-8'))
                            print('# CONNECTION ID: %s # "%s" reposted!' % (CONNID, content))
                            i = i + 1

                        # 关闭

                        disconnectMsg = disconnect(CONNID)
                        self.request.sendall(disconnectMsg.tostring().encode('utf-8'))
                        print('# Disconnection Message sent!')


def resolveError():
    print('Command Error!')
    print('Format: listen.py -p <portnumber> -u <u1:p1><u2:p2>...')


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hp:u:")
    except getopt.GetoptError:
        resolveError()
        sys.exit(2)
    if opts[0][0] == '-h' and len(opts) == 1:
        print('Format: listen.py -p <portnumber> -u <u1:p1><u2:p2>...')
        sys.exit()
    elif opts[0][0] == '-h' and len(opts) != 1:
        resolveError()
        sys.exit(2)
    else:
        if len(args) == 0:
            usrpswd = opts[1][1].split(',')
            for i in usrpswd:
                if i.find(':') == -1:
                    resolveError()
            ###
            # begin
            ###
            port = opts[0][1]
            for i in usrpswd:
                temp = i.split(':')
                tempUsr = {}
                tempUsr['username'] = temp[0]
                tempUsr['password'] = temp[1]
                userInfo.append(tempUsr)
            # print(userInfo)
            print('\n# 向内监听端口为' + port)
            HOST = '127.0.0.1'
            PORT = int(port)
            ADDR = (HOST, PORT)
            server = ThreadingTCPServer(ADDR, Handler)  # 参数为监听地址和已建立连接的处理类
            print('# Server start!\n# Waiting for TCP connection...\n')
            server.serve_forever()  # 监听，建立好TCP连接后，为该连接创建新的socket和线程，并由处理类中的handle方法处理

        else:
            resolveError()
            sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
