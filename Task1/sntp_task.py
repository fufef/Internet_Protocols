import socket
import datetime
from datetime import datetime
from datetime import timedelta


def main():
    port = 123
    host = "127.0.0.1"
    with open("config.txt") as f:
        try:
            time_delay = int(f.readline())
        except ValueError:
            print("Время должно быть целым числом!")
            return

    sock = socket.socket(socket.SOCK_DGRAM)  # socket.SOCK_DGRAM это udp
    sock.bind((host, port))  # привязка сокета к адресу (хосту и порту)
    sock.listen()  # запуск режима прослушивания
    while True:
        conn, address = sock.accept()  # принимает соединение

        with conn:  # чтобы сам открыл-закрыл
            while True:
                data = conn.recv(1024)  # принимает данные по 1кб от клиента в цикле
                if not data:
                    break  # конец если данных больше нет
                elif data == b'/time':
                    time = datetime.now() + timedelta(seconds=time_delay)
                    conn.send(time.strftime("%Y.%m.%d %H:%M:%S").encode())  # отправка времени клиенту
                else:
                    conn.send("Неизвестная команда! Используйте /time для того, чтобы узнать точное время".encode())


if __name__ == '__main__':
    main()
