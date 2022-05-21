import struct

types = {"A": 1, "NS": 1, "MD": 1, "MF": 1, "CNAME": 1, "SOA": 1, }


def get_url(start, data):
    name = b''
    l = data[start]
    while l:
        if l & 0b1100_0000:
            start1 = struct.unpack('!H', data[start:start + 2])[0] & \
                     0b11_1111_1111_1111
            name1 = get_url(start1, data)[0]

            if name:
                name = name1
            else:
                name += b'.' + name1

            return name, start + 2
        else:
            name += b'.' + data[start + 1:start + 1 + l]
            start += l + 1

        l = data[start]

    return name.strip(b'.'), start + 1


class DnsPackage:
    def __init__(self, header, questions, answers, authorities, additionals):
        self.header = header
        self.questions = questions
        self.answers = answers
        self.authorities = authorities
        self.additionals = additionals

    def pack(self):
        res = self.header.pack()

        for i in self.questions + self.answers + self.authorities + \
                 self.additionals:
            res += i.pack()

        return res

    @staticmethod
    def unpack(data):
        true_header = Header.unpack(data[:12])

        start = 12
        questions = []
        for i in range(true_header.qdcount):
            name, start = get_url(start, data)
            name = name.decode('utf-8')
            g = data[start:start + 4]
            qtype, qclass = struct.unpack("!HH", g)
            start += 4
            questions.append(Question(name, qtype, qclass))

        if true_header.qr == 0b0:
            return DnsPackage(true_header, questions, [], [], [])

        answers = []
        for i in range(true_header.ancount):
            name, start = get_url(start, data)
            name = name.decode('utf-8')
            type, clas, ttl, rdlength = struct.unpack("!HHIH",
                                                      data[start:start + 10])
            start += 10
            rdata = data[start:start + rdlength]
            start += rdlength
            answers.append(Answer(name, type, clas, ttl, rdlength, rdata))

        authorities = []
        for i in range(true_header.nscount):
            name, start = get_url(start, data)
            name = name.decode('utf-8')
            type, clas, ttl, rdlength = struct.unpack("!HHIH",
                                                      data[start:start + 10])
            start += 10
            rdata = data[start:start + rdlength]
            start += rdlength
            authorities.append(Answer(name, type, clas, ttl, rdlength, rdata))

        additionals = []
        for i in range(true_header.arcount):
            name, start = get_url(start, data)
            name = name.decode('utf-8')
            type, clas, ttl, rdlength = struct.unpack("!HHIH",
                                                      data[start:start + 10])
            start += 10
            rdata = data[start:start + rdlength]
            start += rdlength
            additionals.append(Answer(name, type, clas, ttl, rdlength, rdata))

        return DnsPackage(true_header, questions, answers, authorities,
                          additionals)


class Header:
    def __init__(
            self, id, qr, qpcode, aa, tc, rd, ra, z, rcode, qdcount,
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

    def pack(self):
        third_fourth_bytes_value = \
            self.qr << 15 | self.qpcode << 11 | self.aa << 10 | \
            self.tc << 9 | self.rd << 8 | self.ra << 7 | self.z << 6 | \
            self.rcode

        return struct.pack("!6H", self.id, third_fourth_bytes_value,
                           self.qdcount, self.ancount, self.nscount,
                           self.arcount)

    @staticmethod
    def unpack(data):
        _bytes = struct.unpack("!6H", data)
        return Header(_bytes[0], _bytes[1] >> 15, _bytes[1] >> 11 & 0b1111,
                      _bytes[1] >> 10 & 0b1, _bytes[1] >> 9 & 0b1,
                      _bytes[1] >> 8 & 0b1, _bytes[1] >> 7 & 0b1,
                      _bytes[1] >> 4 & 0b111, _bytes[1] & 0b1111, _bytes[2],
                      _bytes[3], _bytes[4], _bytes[5])


class Question:
    def __init__(self, qname, qtype, qclass):
        self.qname = qname
        self.qtype = qtype
        self.qclass = qclass

    def pack(self):
        res = b''

        for a in self.qname.strip('.').split('.'):
            res += struct.pack("!B", len(a)) + a.encode()

        return res + struct.pack("!BHH", 0b0, self.qtype, self.qclass)

    def __eq__(self, other):
        return self.qname == other.qname and self.qtype == other.qtype and \
               self.qclass == other.qclass

    def __hash__(self):
        return ((hash(self.qname) * 69127) + hash(self.qtype)) * 69127 + \
               hash(self.qclass)


class Answer:
    def __init__(self, name, type, clas, ttl, rdlength, rdata):
        self.name = name
        self.type = type
        self.clas = clas
        self.ttl = ttl
        self.rdlength = rdlength
        self.rdata = rdata

    def pack(self):
        res = b''

        for a in self.name.strip('.').split('.'):
            res += struct.pack("!B", len(a)) + a.encode()

        return res + struct.pack("!BHHIH", 0b0, self.type, self.clas,
                                 self.ttl, self.rdlength) + self.rdata
