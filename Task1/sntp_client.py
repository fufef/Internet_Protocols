import socket, struct, sys, time

host = '127.0.0.1'
port = 123
TIME1970 = 2208988800


def sntp_client():
    client = socket.socket()
    client.connect((host, port))
    data = b'\x1b' + 47 * b'\0'
    client.send(data)
    data = client.recv(1024)
    if data:
        t = struct.unpack('!12I', data)[10] - TIME1970 - 5 * 3600
        print(time.ctime(t))


if __name__ == '__main__':
    sntp_client()
