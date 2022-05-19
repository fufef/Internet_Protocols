import socket
import struct
import dns_structure

host = '127.0.0.1'
port = 53


def sntp_client():
    client = socket.socket()
    client.connect((host, port))
    header = dns_structure.Header(1, 0, 0, 1, 0, 0)
    data = dns_structure.DnsPackage()
    client.send(data)
    data = client.recv(1024)
    if data:
        t = struct.unpack('!12I', data)
        print(t)


if __name__ == '__main__':
    sntp_client()
