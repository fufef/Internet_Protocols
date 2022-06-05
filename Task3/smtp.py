import base64
import socket
import ssl
from pathlib import Path

from settings import *


def request(sock, request):
    sock.send((request + '\n').encode())
    recv_data = sock.recv(65535).decode()
    return recv_data


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((host_addr, port))
    client = ssl.wrap_socket(client)
    print(client.recv(1024).decode())
    print(request(client, 'ehlo myUserName'))

    base64login = base64.b64encode(user_name.encode()).decode()
    base64password = base64.b64encode(password.encode()).decode()

    print(request(client, 'AUTH LOGIN'))
    print(request(client, base64login))
    print(request(client, base64password))

    print(request(client, 'MAIL FROM:IvanTestMail3@yandex.ru'))
    print(request(client, "RCPT TO:IvanTestMail3@yandex.ru"))
    print(request(client, 'DATA'))

    msg = ''

    with open('headers.txt') as f:
        msg += f.read()

    msg += '\n'

    bound = '--my-bound-mix'

    msg += 'Content-Type: multipart/mixed;' + \
           f'boundary="{bound}"'

    msg += '\n\n'
    msg += f'--{bound}\n'
    msg += 'Content-Type: text/plain\n\n'

    with open('msg.txt') as file:
        msg += file.read() + '\n\n'

    for f in Path('./attachments').iterdir():
        msg += f'--{bound}\n'

        msg += 'Content-Disposition: attachment;\n' + \
               f' filename="{f.name}"\n'
        msg += 'Content-Transfer-Encoding: base64\n'
        msg += 'Content-Type: image/jpeg'
        msg += '\n\n'

        with f.open('rb') as f1:
            msg += base64.b64encode(f1.read()).decode()

        msg += '\n'

    msg += f'--{bound}--'
    msg += '\n.\n'

    print(msg)

    print(request(client, msg))

    # TODO: MIME из словаря, русский subject (очень длинный),
    # обработка ошибок сети, обработка откликов сервера
