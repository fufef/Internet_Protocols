import socket
import dns_structure
import struct


def receive_data(server, data_from_client):
    sock_for_root = socket.socket()
    sock_for_root.connect((server, 53))
    pack_to_root = dns_structure.DnsPackage(
        data_from_client.header, data_from_client.questions, [], [], []).pack()
    sock_for_root.send(pack_to_root)
    data_from_root = dns_structure.DnsPackage.unpack(sock_for_root.recv(1024))

    return data_from_root


def main():
    port = 53
    host = "127.0.0.1"
    cache = set()
    servers = set()

    sock = socket.socket(socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.listen()
    while True:
        conn, address = sock.accept()

        with conn:
            while True:
                data = conn.recv(1024)
                if data:
                    data_from_client = dns_structure.DnsPackage.unpack(data)

                    sock_for_root = socket.socket()
                    sock_for_root.connect(("192.203.230.10", 53))
                    pack_to_root = dns_structure.DnsPackage(
                        data_from_client.header, data_from_client.questions, [], [], []).pack()
                    sock_for_root.send(pack_to_root)
                    data_from_root = dns_structure.DnsPackage.unpack(sock_for_root.recv(1024))

                    d = data_from_root
                    ans = []
                    while len(d.answers) == 0:
                        next_ip = '.'.join(map(str, d.authorities[0].rdata))
                        d = receive_data(next_ip, d).unpack()


                    pack_to_client = d.pack()
                        # dns_structure.DnsPackage(
                        # data_from_client.header, data_from_client.questions, ans,
                        # data_from_root.authorities, data_from_root.additionals).pack()

                    conn.send(pack_to_client)
                else:
                    break


if __name__ == '__main__':
    port = 53
    host = "127.0.0.1"
    cache = set()
    servers = set()

    sock = socket.socket(socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.listen()
    conn, address = sock.accept()

    with conn:
        pack_to_client = dns_structure.DnsPackage()
        conn.send(pack_to_client)


    #main()
