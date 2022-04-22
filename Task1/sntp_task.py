import datetime
import socket
import struct
from datetime import datetime
from datetime import timedelta


def tmp(seconds):
    a = 0.5
    res = 0
    
    for i in range(32):
        res *= 2
        
        if seconds >= a:
            seconds -= a
            res += 1
            
        a /= 2
    return res


def _get_ntp_time_offset_in_tuple(date):
    offset = (date - datetime(1900, 1, 1)).total_seconds()
    seconds = int(offset)
    return seconds % (2 ** 32), tmp(offset % 1)


def unpack_input_bytes(data: bytes):
    res = struct.unpack('!B39xII', data)
    return (res[0] >> 3) & 0b111, (res[1], res[2])
    

def create_pack(version, originate_timestamp, time):
    li = 0  # индикатор коррекции, информация о последней секунде в минутеx
    mode = 4  # режим (сервер)
    first_byte_as_char = (li << 6) | (version << 3) | mode

    stratum = 3  # страта - уровень локальных часов
    poll = 4  # макс интервал между сообщениями серверу
    # точность  часов в секундах до ближайшей степени двойки
    precision = 0
    root_delay = 0  # задержка
    root_dispersion = 0  # погрешность дисперсия
    reference_identifier = 0  # идентификатор источника
    reference_timestamp = time  # время обновления - когда сист часы были скорректированы
    receive_timestamp = time  # временная мека получения запроса
    transmit_timestamp = time  # отметка времени передачи

    pack = struct.pack('!3BbIIIIIIIIIII', first_byte_as_char, stratum, poll, precision, root_delay,
                       root_dispersion, reference_identifier, *reference_timestamp, *originate_timestamp,
                       *receive_timestamp, *transmit_timestamp)
    return pack


def main():
    port = 123
    host = "127.0.0.1"
    with open("config.txt") as f:
        try:
            time_delay = timedelta(seconds=int(f.readline()))
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
                if data:
                    version, transmit_timestamp = unpack_input_bytes(data)
                    time = datetime.now() + time_delay
                    receive_timestamp = _get_ntp_time_offset_in_tuple(time)
                    pack = create_pack(version, transmit_timestamp, receive_timestamp)

                    conn.send(pack)  # отправка времени клиенту
                else:
                    break


if __name__ == '__main__':
    main()
