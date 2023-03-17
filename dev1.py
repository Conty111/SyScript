import datetime
import socket
import csv

from pythonping import ping
from socket import AF_INET, SOCK_STREAM


sock = socket.socket(AF_INET, SOCK_STREAM)

TIMEOUT_PING = 4
TIMEOUT_SOCKET = 4
COUNT_OF_PACKET = 4


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
        test = Checked_sockets(address, ports)
        self.date.append(test.characteristics["date"])
        self.rtt.append(test.characteristics["rtt"])
        self.packet_loss.append(test.characteristics["packet_loss"])
        self.port_status.append(test.characteristics["port_status"])
        self.port.append(test.port)
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
            port_status = "Ports are missing"
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
                row.insert(0, "Address hasn't hostname")
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
    ping_adr = ping(address, timeout=TIMEOUT_PING, count=COUNT_OF_PACKET)
    rtt = ping_adr.rtt_avg_ms
    packet_loss = ping_adr.packet_loss
    sock = socket.socket(AF_INET, SOCK_STREAM)
    sock.settimeout(TIMEOUT_SOCKET)
    date = datetime.datetime.now().isoformat().replace("T", " ")
    try: #Проверяем открытость порта
        sock.connect((address, port))
        port_status = "Opened"
    except:
        port_status = "Not opened"
    return {"rtt": rtt,
            "packet_loss": float(packet_loss),
            "port_status": port_status,
            "date": date}


def get_domain_adr(adr: str) -> str:
    try:
        return socket.gethostbyname_ex(adr)[2]
    except:
        return "Error in domain adress"


with open("test.csv", newline='') as csvfile:
    file_input = csv.reader(csvfile, delimiter=";")
    for row in file_input:
        if row:
            row = make_adr_from_row(row)
            if row != []:
                row_of_addresses = Checked_row(row)
                row_of_addresses.show()
