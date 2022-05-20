import socket
from datetime import datetime, timedelta

import dns_structure


def receive_data(server, data_from_client):
    sock_for_root = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pack_to_root = dns_structure.DnsPackage(
        data_from_client.header, data_from_client.questions, [], [], [])
    sock_for_root.sendto(pack_to_root.pack(), (server, 53))
    data_from_root = dns_structure.DnsPackage.unpack(
        sock_for_root.recvfrom(1024)[0])

    return data_from_root


def main():
    port = 53
    host = "127.0.0.1"
    cache = dict()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    while True:
        data, address = sock.recvfrom(1024)

        if data:
            data_from_client = dns_structure.DnsPackage.unpack(data)
            sock_for_root = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            ans = []
            add = []
            auth = []
            for q in data_from_client.questions:
                if q in cache:
                    q_ans, q_add, q_auth, time_limit = cache[q]

                    if datetime.now() < time_limit:
                        ans += q_ans
                        add += q_add
                        auth += q_auth
                        continue

                pack_to_root = dns_structure.DnsPackage(
                    data_from_client.header, [q], [], [], []).pack()
                sock_for_root.sendto(pack_to_root, ("192.203.230.10", 53))
                data_from_root = dns_structure.DnsPackage.unpack(
                    sock_for_root.recvfrom(1024)[0])

                d = data_from_root
                while d.header.ancount == 0:
                    r = list(filter(lambda x: x.type == 1, d.additionals))

                    if len(r) == 0:
                        r = list(filter(lambda x: x.type == 2, d.authorities))

                    next_ip = '.'.join(map(str, r[0].rdata))
                    d = receive_data(next_ip, data_from_client)

                cache[q] = (d.answers, d.additionals, d.authorities,
                            datetime.now() +
                            timedelta(seconds=d.answers[0].ttl))

                ans += d.answers
                add += d.additionals
                auth += d.authorities

            req_header = data_from_client.header
            ans_header = dns_structure.Header(
                req_header.id, 1, req_header.qpcode, 0, req_header.tc,
                req_header.rd, 1, req_header.z, req_header.rcode,
                req_header.qdcount, len(ans), len(auth), len(add))

            pack_to_client = dns_structure.DnsPackage(
                ans_header, data_from_client.questions, ans, auth, add)

            a = pack_to_client.pack()
            sock.sendto(a, address)


if __name__ == '__main__':
    main()
