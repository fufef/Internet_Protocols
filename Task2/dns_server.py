import socket
from datetime import datetime, timedelta

import dns_structure

ROOT_SERVER_IP = "198.41.0.4"


def receive_data(server, data_from_client):
    sock_for_root = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pack_to_root = dns_structure.DnsPackage(
        data_from_client.header, data_from_client.questions, [], [], [])
    sock_for_root.sendto(data_from_client.pack(), (server, 53))
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
                sock_for_root.sendto(pack_to_root, (ROOT_SERVER_IP, 53))
                data_from_root = dns_structure.DnsPackage.unpack(
                    sock_for_root.recvfrom(1024)[0])

                d = data_from_root
                while d.header.ancount == 0:
                    r = list(filter(lambda x: x.type == 1, d.additionals))

                    if len(r) > 0:
                        next_ip = '.'.join(map(str, r[0].rdata))
                    else:
                        r = list(filter(lambda x: x.type == 2, d.authorities))

                        if len(r) == 0:
                            break

                        domain = dns_structure.get_url(0, r[0].rdata)[0] \
                            .decode()
                        next_ip = ROOT_SERVER_IP

                        while d.header.ancount == 0:
                            sub_q = dns_structure.Question(domain, 1, 1)
                            pack = dns_structure.DnsPackage(
                                data_from_client.header, [sub_q], [], [], [])

                            d = receive_data(next_ip, pack)

                            r = list(
                                filter(lambda x: x.type == 1, d.additionals))
                            next_ip = '.'.join(map(str, r[0].rdata))

                        next_ip = '.'.join(map(str, d.answers[0].rdata))

                    d = receive_data(next_ip, data_from_client)

                ttl = min((x.ttl
                           for x in d.answers + d.additionals + d.authorities),
                          default=0)

                cache[q] = (d.answers, d.additionals, d.authorities,
                            datetime.now() + timedelta(seconds=ttl))

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
