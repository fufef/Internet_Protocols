import base64
import re
import socket
import ssl
from pathlib import Path
from settings import USER_NAME, PASSWORD, HOST_ADDR, PORT, RECIPIENT

mime_dict = {'image': ['image/jpeg', 'image/webp', 'image/bmp', 'image/png', 'image/gif', 'image/pjpeg'],
             'text': ['text/plain', 'text/html', 'text/css', 'text/csv', 'text/cmd', 'text/php', 'text/javascript'],
             'video': ['video/mpeg', 'video/mp4', 'video/webm'],
             'audio': ['audio/mp4', 'audio/webm', 'audio/vnd.wave', 'audio/mpeg', 'audio/aac'],
             'application': ['application/pdf', 'application/xml', 'application/msword', 'application/json',
                             'application/zip', 'application/ogg'],
             'multipart': ['multipart/mixed', 'multipart/alternative'],
             'model': ['model/example', 'model/mesh', 'model/x3d+xml', 'model/iges']}

smtp_responses = {555: 'MAIL FROM/RCPT TO parameters not recognized or not implemented',
                  554: 'Transaction failed или No SMTP service here',
                  553: 'Requested action not taken: mailbox name not allowed',
                  550: 'Requested mail action not taken: mailbox unavailable',
                  535: 'Authentication failed',
                  500: 'Syntax error, command unrecognized',
                  455: 'Server unable to accommodate parameters',
                  451: 'Requested action aborted: error in processing',
                  450: 'Requested mail action not taken: mailbox unavailable',
                  250: 'Requested mail action okay, completed'}


def check_response(req, is_end=False):
    code = int(re.split(' |-', req)[0])
    if code == 250 and not is_end:
        return
    if code in smtp_responses:
        print(smtp_responses[code])


def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False


def request(sock, req):
    sock.send((req + '\n').encode())
    recv_data = sock.recv(65535).decode()
    return recv_data


def main():
    if not is_connected():
        print('Please check your Internet connection')
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST_ADDR, PORT))
        client = ssl.wrap_socket(client)
        client.recv(1024).decode()
        check_response(request(client, 'ehlo myUserName'))

        base64login = base64.b64encode(USER_NAME.encode()).decode()
        base64password = base64.b64encode(PASSWORD.encode()).decode()

        check_response(request(client, 'AUTH LOGIN'))

        check_response(request(client, base64login))

        check_response(request(client, base64password))

        check_response(request(client, f'MAIL FROM:{USER_NAME}'))

        check_response(request(client, f"RCPT TO:{RECIPIENT}"))

        check_response(request(client, 'DATA'))

        msg = ''

        with open('headers.txt', 'r', encoding='utf-8') as f:
            msg += f.read()

        msg += '\n'

        bound = '--my-bound-mix'

        msg += f'Content-Type: {mime_dict["multipart"][0]};' + \
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

        # print(msg)

        check_response(request(client, msg), True)


if __name__ == '__main__':
    main()
