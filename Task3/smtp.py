import base64
import socket
import ssl
from pathlib import Path
from settings import USER_NAME, PASSWORD, HOST_ADDR, PORT, RECIPIENT

mime_dict = {'image': ['image/jpeg', 'image/webp', 'image/bmp', 'image/png', 'image/gif'],
             'text': ['text/plain', 'text/html', 'text/css', 'text/calendar', 'text/javscript'],
             'video': ['video/mpeg'],
             'application': ['application/json', 'application/gzip']}


def request(sock, req):
    sock.send((req + '\n').encode())
    recv_data = sock.recv(65535).decode()
    return recv_data


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST_ADDR, PORT))
        client = ssl.wrap_socket(client)
        client.recv(1024).decode()
        request(client, 'ehlo myUserName')

        base64login = base64.b64encode(USER_NAME.encode()).decode()
        base64password = base64.b64encode(PASSWORD.encode()).decode()

        request(client, 'AUTH LOGIN')
        request(client, base64login)
        request(client, base64password)
        request(client, f'MAIL FROM:{USER_NAME}')
        request(client, f"RCPT TO:{RECIPIENT}")
        request(client, 'DATA')

        msg = ''

        with open('headers.txt', 'r', encoding='utf-8') as f:
            msg += f.read()

        msg += '\n'

        bound = '--my-bound-mix'

        msg += 'Content-Type: multipart/mixed;' + \
               f'boundary="{bound}"'

        msg += '\n\n'
        msg += f'--{bound}\n'
        msg += f'Content-Type: {mime_dict["text"][0]}\n\n'

        with open('msg.txt', 'r', encoding='utf-8') as file:
            msg += file.read() + '\n\n'

        for f in Path('./attachments').iterdir():
            msg += f'--{bound}\n'

            msg += 'Content-Disposition: attachment;\n' + \
                   f' filename="{f.name}"\n'
            msg += 'Content-Transfer-Encoding: base64\n'
            msg += f'Content-Type: {mime_dict["image"][0]}'
            msg += '\n\n'

            with f.open('rb') as f1:
                msg += base64.b64encode(f1.read()).decode()

            msg += '\n'

        msg += f'--{bound}--'
        msg += '\n.\n'

        print(msg)

        request(client, msg)


if __name__ == '__main__':
    main()
