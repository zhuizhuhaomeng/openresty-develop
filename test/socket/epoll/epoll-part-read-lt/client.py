import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddr = ('127.0.0.1',8080)
client.connect(serverAddr)

sendData='01234567890123456789'
print("send: %s" % sendData)
client.send(sendData.encode())

client.settimeout(5.0)
print('receive:', end = '', flush=True)


while True:
    try:
        recvData = client.recv(1024)
        if not recvData:
            break
        print('%s' % recvData.decode("utf-8"), end = '', flush=True)
    except socket.timeout:
        print('\nexception: socket timeout')
        break
client.close()
print('close socket!')
