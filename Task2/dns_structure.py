import struct


types = {"A": 1, "NS": 1, "MD":1, "MF": 1, "CNAME": 1, "SOA": 1, }

def _get_url(start, data):
    name = b""
    l = data[start]
    while l:
        if l & 0b1100_0000:
            start1 = int.from_bytes(data[start:start + 2], 'big') & 0b11_1111_1111_1111
            name1, _ = _get_url(start1, data)
            return name1 + b'.' + name, start + 2
        else:
            name += b'.' + data[start + 1:start + 1 + l]
            start += l + 1

        l = data[start]

    return name.lstrip(b'.'), start + 1


class DnsPackage:
    def __init__(self, header, questions, answers, authorities, additionals):
        self.header = header
        self.questions = questions
        self.answers = answers
        self.authorities = authorities
        self.additionals = additionals

    def pack(self):
        res = struct.pack("!6H", self.header.id, self.header.qr << 15 | self.header.qpcode << 11 |
                          self.header.aa << 10 | self.header.tc << 9 | self.header.rd << 8 | self.header.ra << 7 |
                          self.header.z << 6 | self.header.rcode, self.header.qdcount, self.header.ancount,
                          self.header.nscount, self.header.arcount)
        for i in self.questions:
            ar = i.qname.split('.')
            for a in ar:
                b = a.encode('utf-8')
                res += struct.pack("!B", len(a)) + b
            res += struct.pack("!B", 0b0)
            res += struct.pack("!HH", i.qtype, i.qclass)

        if self.header.qr == 0b0:
            return res

        return res

    def create_answer(self):
        ''''dffffffffffffffffff'''

        struct.pack('', self.header)

    def create_question(self, qname, qtype, qclass):
        return struct.pack("!" + "HH")

    @staticmethod
    def unpack(data):
        header = struct.unpack("!6H", data[0:12])
        true_header = Header(header[0], header[1] >> 15, header[1] >> 11 & 0b1111, header[1] >> 10 & 0b1,
                             header[1] >> 9 & 0b1, header[1] >> 8 & 0b1, header[1] >> 7 & 0b1, header[1] >> 6 & 0b111,
                             header[1] & 0b1111, header[2], header[3], header[4], header[5])
        start = 12
        questions = []
        for i in range(true_header.qdcount):
            name, start = _get_url(start, data)
            name = name.decode('utf-8')
            g = data[start:start + 4]
            qtype, qclass = struct.unpack("!HH", g)
            start += 4
            questions.append(Question(name, qtype, qclass))

        if true_header.qr == 0b0:
            return DnsPackage(true_header, questions, [], [], [])

        answers = []
        for i in range(true_header.ancount):
            name, start = _get_url(start, data)
            name = name.decode('utf-8')
            type, clas, ttl, rdlength = struct.unpack("!HHIH", data[start:start + 10])
            start += 10
            rdata = data[start:start+rdlength]
            start += rdlength
            answers.append(Answer(name, type, clas, ttl, rdlength, rdata))

        authorities = []
        for i in range(true_header.nscount):
            name, start = _get_url(start, data)
            name = name.decode('utf-8')
            type, clas, ttl, rdlength = struct.unpack("!HHIH", data[start:start + 10])
            start += 10
            rdata = data[start:start + rdlength]
            start += rdlength
            authorities.append(Answer(name, type, clas, ttl, rdlength, rdata))

        additionals = []
        for i in range(true_header.arcount):
            name, start = _get_url(start, data)
            name = name.decode('utf-8')
            type, clas, ttl, rdlength = struct.unpack("!HHIH", data[start:start + 10])
            start += 10
            rdata = data[start:start + rdlength]
            start += rdlength
            additionals.append(Answer(name, type, clas, ttl, rdlength, rdata))

        return DnsPackage(true_header, questions, answers, authorities, additionals)


class Header:
    def __init__(self, id, qr, qpcode, aa, tc, rd, ra, z, rcode, qdcount,
                 ancount, nscount, arcount):
        self.id = id
        self.qr = qr
        self.qpcode = qpcode
        self.aa = aa
        self.tc = tc
        self.rd = rd
        self.ra = ra
        self.z = z
        self.rcode = rcode
        self.qdcount = qdcount
        self.ancount = ancount
        self.nscount = nscount
        self.arcount = arcount


class Question:
    def __init__(self, qname, qtype, qclass):
        self.qname = qname
        self.qtype = qtype
        self.qclass = qclass


class Answer:
    def __init__(self, name, type, clas, ttl, rdlength, rdata):
        self.name = name
        self.type = type
        self.clas = clas
        self.ttl = ttl
        self.rdlength = rdlength
        self.rdata = rdata
