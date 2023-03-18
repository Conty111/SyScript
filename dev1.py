import datetime
import socket
import csv
import time

from config import FILE_TO_READ, TIMEOUT_PING, COUNT_OF_PACKET, TIMEOUT_SOCKET, OPENED, \
    DOMAIN_ERROR, MISSING_PORTS, NOT_OPENED, NOT_HOSTNAME, NOT_INTERNET_CONNECTION
from socket import AF_INET, SOCK_STREAM
from pythonping import ping


t1 = time.time()
class Checked_row:
    def __init__(self, host_row: list):
        self.domain = host_row[0]
        self.date = []
        self.ip_address = []
        self.packet_loss = []
        self.rtt = []
        self.port = []
        self.port_status = []

        for address in host_row[1]:
            self.set_data(host_row[2], address)

    def set_data(self, ports: list, address: str):
        all_info = Checked_sockets(address, ports)
        self.date.append(all_info.characteristics["date"])
        self.rtt.append(all_info.characteristics["rtt"])
        self.packet_loss.append(all_info.characteristics["packet_loss"])
        self.port_status.append(all_info.characteristics["port_status"])
        self.port.append(all_info.port)
        self.ip_address.append(address)

    def show(self):
        for i in range(len(self.ip_address)):
            result = self.date[i]
            result += ' | ' + self.domain
            result += ' | ' + self.ip_address[i]
            result += ' | ' + str(self.packet_loss[i])
            result += ' | ' + str(self.rtt[i]) + ' ms'
            result += ' | ' + str(self.port[i])
            result += ' | ' + str(self.port_status[i])
            print(result)
        print("\n")


class Checked_sockets:
    def __init__(self, address, ports=False) -> None:
        if not ports:
            date = datetime.datetime.now().isoformat().replace("T", " ")
            ping_adr = ping(address, count=COUNT_OF_PACKET, timeout=TIMEOUT_PING)
            rtt = ping_adr.rtt_avg_ms
            packet_loss = ping_adr.packet_loss
            port_status = MISSING_PORTS
            self.port = -1
            self.characteristics = {"date": date,
                                    "rtt": rtt,
                                    "packet_loss": packet_loss,
                                    "port_status": port_status}
        else:
            for port in ports:
                self.characteristics = get_socket_characteristics(address, int(port))
                self.port = port


def make_adr_from_row(row: list) -> list:
    # Преобразование в формат ['доменное имя', ['IP-адреса'], ['порты']]
    if "." in row[0] or row[0] == 'localhost':
        # Проверка: дано доменное имя или ip-адерс
        if not (row[0].replace(".", "", len(row[0]))).isdigit():
            row.insert(1, get_domain_adr(row[0]))
        else:
            try:
                # Пытаемся добавить имя хоста/доменное имя, если оно есть
                row.insert(0, socket.gethostbyaddr(row[0]))
            except:
                row.insert(0, NOT_HOSTNAME)
            row[1] = [row[1]]

        # Проверка на корректность введенных портов
        if (row[2].replace(",", "", len(row[2]))).isdigit():
            row[2] = row[2].split(",")
        else:
            row[2] = []

        return row
    else:
        return []


def get_socket_characteristics(address: str, port: int) -> dict:
    try: #Проверяем соединение с интернетом
        ping_adr = ping(address, timeout=TIMEOUT_PING, count=COUNT_OF_PACKET)
    except:
        return NOT_INTERNET_CONNECTION
    
    rtt = ping_adr.rtt_avg_ms
    packet_loss = ping_adr.packets_lost
    date = datetime.datetime.now().isoformat().replace("T", " ")
    sock = socket.socket(AF_INET, SOCK_STREAM)
    sock.settimeout(TIMEOUT_SOCKET)
    try: #Проверяем открытость порта
        sock.connect((address, port))
        port_status = OPENED
    except:
        port_status = NOT_OPENED
    return {"rtt": rtt,
            "packet_loss": float(packet_loss),
            "port_status": port_status,
            "date": date}


def get_domain_adr(adr: str) -> str:
    try:
        return socket.gethostbyname_ex(adr)[2]
    except:
        return DOMAIN_ERROR


with open(FILE_TO_READ, newline='') as csvfile:
    for row in csv.reader(csvfile, delimiter=";"):
        if row:
            row = make_adr_from_row(row)
            if row != []:
                row_of_addresses = Checked_row(row)
                row_of_addresses.show()

t2 = time.time()
print(t2 - t1)