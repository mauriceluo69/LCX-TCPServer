import sys
import getopt
import socket
import random
import uuid
import time


from init import *


def isColonin(string):
    if string.find(':') == -1:
        return False
    else:
        return True


def resolveError():
    print('Command Error!')
    print('Format: slave.py -r <ip:port1> -u <u1:p1> -p port2 -l <ip:port3>')


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hr:u:p:l:")
        # print(opts)
        # print(args)
    except getopt.GetoptError:
        resolveError()
        sys.exit(2)
    if opts[0][0] == '-h' and len(opts) == 1:
        print('Format: slave.py -r <ip:port1> -u <u1:p1> -p port2 -l <ip:port3>')
        sys.exit()
    elif opts[0][0] == '-h' and len(opts) != 1:
        resolveError()
        sys.exit(2)
    else:
        if len(args) == 0:
            if isColonin(opts[0][1]) and isColonin(opts[1][1]) and isColonin(opts[3][1]):
                ###
                # Go
                ###
                print("\n# Start TCP connection...")

                remoteListenInternalLocation = {}
                temp = opts[0][1].split(':')
                remoteListenInternalLocation['ip'] = temp[0]
                remoteListenInternalLocation['port'] = temp[1]
                # print(remoteListenInternalLocation)

                user = {}
                temp = opts[1][1].split(':')
                user['username'] = temp[0]
                user['password'] = temp[1]
                # print(user)

                remoteListenPort = opts[2][1]
                # print(remoteListenPort)

                localServerListenLocation = {}
                temp = opts[3][1].split(':')
                localServerListenLocation['ip'] = temp[0]
                localServerListenLocation['port'] = temp[1]
                # print(localServerListenLocation)
                HOST = remoteListenInternalLocation['ip']
                PORT = int(remoteListenInternalLocation['port'])
                ADDR = (HOST, PORT)
                sock = socket.socket()

                try:
                    sock.connect(ADDR)
                    print('# Connected with server\n')
                    # CHAP
                    randomUUID = str(uuid.uuid1())  # len = 36
                    saltstr = randomUUID + user['username']
                    chap1 = chap_salt(len(saltstr), saltstr)
                    sock.sendall(chap1.tostring().encode('utf-8'))
                    print('# CHAP Challenge message sent')

                    recvChap2 = sock.recv(BUF_SIZE).decode('utf-8')
                    if recvChap2 == noSuchUserErrorMsg:
                        print(noSuchUserErrorMsg)
                        print('# Closing...')
                        sys.exit(2)
                    print('# CHAP Hash message received')
                    if resolve(recvChap2)[2] == genearteMD5(randomUUID + user['password']):
                        print('# Hash configuration passed')
                        chap3 = chap_result(True)
                        sock.sendall(chap3.tostring().encode('utf-8'))
                        print('# CHAP Result message sent')
                    else:
                        print(hashFailedErrorMsg)                   
                        chap3 = chap_result(False)
                        sock.sendall(chap3.tostring().encode('utf-8'))
                        print('# CHAP Result message sent')
                        print('# Closing...')
                        sys.exit(2)
                    print(hashSuccessMsg)
                    
                    # Bind
                    rID = str(random.randint(10000, 99999))
                    sock.sendall(bind_request(rID, remoteListenPort).tostring().encode('utf-8'))
                    print("# Bind Request No.%s message sent" % rID)
                    recvBind2 = resolve(sock.recv(BUF_SIZE).decode('utf-8'))
                    if recvBind2[2] == "True":
                        print("# Bind Request No.%s accepted!\n# Remote Listen server is ready to listen Port: %s\n" % (recvBind2[1], recvBind2[3]))
                    else:
                        print("# Bind Request No.%s denied!\n# Error: Remote Listen server is unable to listen Port: %s" % (recvBind2[1], recvBind2[3]))
                        print("# Connection refused!\n# Closing...")
                        sys.exit(2)
                    print('# Waiting for connection request...\n')

                    # Connect
                    recvConn1 = resolve(sock.recv(BUF_SIZE).decode('utf-8'))
                    print("# Connection Request No. %s received" % recvConn1[1])
                    print('# Connecting %s:%s...' % (localServerListenLocation['ip'], localServerListenLocation['port']))
                    obj = socket.socket()
                    try:
                        ###

                        obj.connect((localServerListenLocation['ip'], int(localServerListenLocation['port'])))

                        ###
                    except Exception:
                        print("# Error: Connection failed")
                        # huisong
                        conn2 = connect_response(recvConn1[1], False, '00000')
                        sock.sendall(conn2.tostring().encode('utf-8'))
                        # print(conn2.tostring())
                        print('# Closing...')
                        sys.exit(2)
                    print("# Connection success")
                    # huisong
                    CONNID = random.randint(10000, 99999)
                    conn2 = connect_response(recvConn1[1], True, CONNID)
                    sock.sendall(conn2.tostring().encode('utf-8'))
                    print('# Connect Response No. %s sent' % recvConn1[1])
                    print('\n# IMPORTANT # Data tranfer begin\n# CONNECTION_ID = %d\n' % CONNID)

                    # data trans
                    i = 1
                    while i <= TIMES:
                        recvData = resolve(sock.recv(BUF_SIZE).decode('utf-8'))
                        connID = recvData[1]
                        content = recvData[2]
                        print('# CONNECTION ID: %s # "%s" reposted!' % (connID, content))
                        obj.sendall(content.encode('utf-8'))
                        i = i + 1

                    i = 1
                    while i <= TIMES:
                        _data = obj.recv(BUF_SIZE).decode('utf-8')
                        toLocal = data(CONNID, 0, _data)
                        sock.sendall(toLocal.tostring().encode('utf-8'))
                        print('# CONNECTION ID: %s # "%s" reposted!' % (CONNID, _data))
                        i = i + 1

                    print('\n# IMPORTANT # Tranfer test accomplished\n')

                    recvDisc = resolve(sock.recv(BUF_SIZE).decode('utf-8'))
                    print('# CONNECTION ID = %s closed' % recvDisc[1])
                    obj.close()


                except Exception:
                    print('# Error\n')
                    sock.close()
                    sys.exit()
            else:
                resolveError()
        else:
            resolveError()
            sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
