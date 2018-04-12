import socket
import time


from init import *


sk = socket.socket()
sk.bind(("127.0.0.1", 8002))
sk.listen(5)

conn, address = sk.accept()

BUF_SIZE = 1024


i = 1

print('\nWaiting for data from remote client...\n')

while i <= TIMES:
    recvData = conn.recv(BUF_SIZE).decode('utf-8')
    print('# Received Message: "%s"' % recvData)
    i = i + 1

print('\nData tranfer from Remote Clinet to Local Server test accomplished!')
print('Ready to send data to remote client...\n')
i = 1

while i <= TIMES:
    time.sleep(3)
    msg = "Local server message No. " + str(i)
    conn.sendall(msg.encode('utf-8'))
    print("'%s' sent" % msg)
    i = i + 1

print('\nData tranfer from Local Server to Remote Clinet test accomplished!')

conn.close()
