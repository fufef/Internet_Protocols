import socket


def print_success(protocol_suite, port):
    print(f'{protocol_suite} {port}')


def tcp_scan(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((host, port))
        print_success('TCP', port)
    except (socket.timeout, OSError):
        pass


def udp_scan(host, port):
    sock = socket.socket(socket.SOCK_DGRAM)
    sock.settimeout(2)
    try:
        sock.connect((host, port))
        print_success('UDP', port)
    except (socket.timeout, OSError):
        pass


def get_args():
    host, from_port, to_port = input().split()
    try:
        from_port, to_port = int(from_port), int(to_port)
    except ValueError:
        raise Exception('Ports must be integer numbers!')
    if from_port < 0 or to_port > 2 ** 16:
        raise Exception('Ports must be in range 0-65536')
    if to_port - from_port < 0:
        raise Exception('Range of ports must be positive!')
    return host, from_port, to_port


def main():
    host, from_port, to_port = get_args()
    for port in range(from_port, to_port):
        tcp_scan(host, port)
        # udp_scan(host, port)


if __name__ == '__main__':
    main()
