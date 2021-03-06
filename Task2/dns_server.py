import socket
from datetime import datetime, timedelta

import cache_struct
import dns_structure

root = "198.41.0.4"
errors = {
    1: "Cannot understand query structure! ",
    2: "Server Failure! ",
    3: "Non-existent domain! ",
    4: "Cannot execute query of this type! ",
    5: "Security error! "
}
time_pattern = '%d/%m/%Y %H:%M:%S'


def receive_data(server, data_from_client):
    sock_for_root = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_for_root.sendto(data_from_client.pack(), (server, 53))
    sock_for_root.settimeout(2)
    try:
        data_from_root = dns_structure.DnsPackage.unpack(
            sock_for_root.recvfrom(1024)[0])
    except socket.timeout:
        print("Timeout was 2 seconds. Please check Internet connection.")
        return None

    return data_from_root


def main():
    port = 53
    host = "127.0.0.1"
    cache = cache_struct.get_cache()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    while True:
        try:
            data, address = sock.recvfrom(1024)
            if data:
                data_from_client = dns_structure.DnsPackage.unpack(data)
                rcode = data_from_client.header.rcode
                sock_for_root = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                ans = []
                add = []
                auth = []
                for q in data_from_client.questions:
                    qs = q.as_b64_str()

                    if qs in cache:
                        dt = cache[qs]

                        q_ans = [dns_structure.Answer.from_b64_str(i) for i
                                 in dt[0]]
                        q_add = [dns_structure.Answer.from_b64_str(i) for i
                                 in dt[1]]
                        q_auth = [dns_structure.Answer.from_b64_str(i) for i
                                  in dt[2]]
                        time_limit = datetime.strptime(dt[3], time_pattern)

                        if datetime.now() < time_limit:
                            ans += q_ans
                            add += q_add
                            auth += q_auth
                            continue

                    pack_to_root = dns_structure.DnsPackage(
                        data_from_client.header, [q], [], [], []).pack()

                    sock_for_root.sendto(pack_to_root, (root, 53))
                    sock_for_root.settimeout(2)
                    try:
                        data_from_root = dns_structure.DnsPackage.unpack(
                            sock_for_root.recvfrom(1024)[0])
                    except socket.timeout:
                        print(
                            "Timeout was 2 seconds. Please check Internet connection.")
                        break

                    d = data_from_root
                    while d.header.ancount == 0:
                        rcode = d.header.rcode

                        if rcode:
                            print(errors[rcode], "Question was: name=", q.qname,
                                  ", type=", q.qtype, ", class=", q.qclass,
                                  sep="")
                            break

                        r = [x for x in d.additionals if x.type == 1]

                        if len(r) > 0:
                            next_ip = '.'.join(map(str, r[0].rdata))
                        elif d.questions[0].qtype != 2:
                            r = [x for x in d.authorities if x.type == 2]

                            if not r:
                                break

                            domain = dns_structure.get_url(0, r[0].rdata)[0] \
                                .decode()
                            next_ip = root

                            while d.header.ancount == 0:
                                sub_q = dns_structure.Question(domain, 1, 1)
                                pack = dns_structure.DnsPackage(
                                    data_from_client.header, [sub_q], [], [],
                                    [])

                                d = receive_data(next_ip, pack)
                                r = [x for x in d.additionals if x.type == 1]
                                next_ip = '.'.join(map(str, r[0].rdata))

                            next_ip = '.'.join(map(str, d.answers[0].rdata))
                        else:
                            break

                        d = receive_data(next_ip, data_from_client)

                    ttl = min((x.ttl for x in
                               d.answers + d.additionals + d.authorities),
                              default=0)

                    if rcode == 0:
                        dt = [[i.as_b64_str() for i in d.answers],
                              [i.as_b64_str() for i in d.additionals],
                              [i.as_b64_str() for i in d.authorities],
                              (datetime.now() + timedelta(seconds=ttl))
                                  .strftime(time_pattern)]
                        cache[qs] = dt
                        cache_struct.write_in_cache((qs, dt))

                    ans += d.answers
                    add += d.additionals
                    auth += d.authorities

                req_header = data_from_client.header
                ans_header = dns_structure.Header(
                    req_header.id, 1, req_header.qpcode, 0, req_header.tc,
                    req_header.rd, 1, req_header.z, rcode,
                    req_header.qdcount, len(ans), len(auth), len(add))

                pack_to_client = dns_structure.DnsPackage(
                    ans_header, data_from_client.questions, ans, auth, add)

                sock.sendto(pack_to_client.pack(), address)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
