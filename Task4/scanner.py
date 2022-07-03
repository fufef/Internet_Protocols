import socket
import threading


def print_success(protocol_suite, port):
    print(f'{protocol_suite} {port}')


def tcp_scan(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.connect((host, port))
            print_success('TCP', port)
        except (OSError, socket.timeout):
            return


def udp_scan(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(1)
        try:
            sock.sendto(b'helo', (host, port))
            sock.recvfrom(1024)
        except socket.timeout:
            print_success('UDP', port)
        except OSError:
            return


def start_scan(host, port):
    tcp_scan(host, port)
    udp_scan(host, port)


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
        t = threading.Thread(target=start_scan(host, port))
        t.start()


if __name__ == '__main__':
    main()
