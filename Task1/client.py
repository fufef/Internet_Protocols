import socket


port = 123
sock = socket.socket()
sock.connect(('127.0.0.1', port))
sock.send(b'/time')

data = sock.recv(1024)
sock.close()

print(data.decode())
