import socket
import struct

import dns_structure

host = '127.0.0.1'
port = 53


def create_pack():
    id = 1
    qr = 0
    qpcode = 0
    # aa - ignore
    tc = 0
    rd = 1
    #ra - ignore
    z = 0
    #rcode - ignore
    qdcount = 0 ###todo
    #ancount - ignore
    #ncount - ign
    #arcount - ign

    qname = "02 vk 03 com"
    qtype ='A'
    qclass = 'IN'

    struct.pack('', id)

def sntp_client():
    client = socket.socket()
    client.connect((host, port))
    header = dns_structure.Header(1, 0, 0, 1, )
    data = dns_structure.DnsPackage()
    client.send(data)
    data = client.recv(1024)
    if data:
        t = struct.unpack('!12I', data)
        print(t)


if __name__ == '__main__':
    sntp_client()
