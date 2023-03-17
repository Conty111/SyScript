import csv
import socket
import datetime
from pythonping import ping
from socket import AF_INET, SOCK_STREAM



sock = socket.socket(AF_INET, SOCK_STREAM)

TIMEOUT_PING = 4
TIMEOUT_SOCKET = 4
COUNT_OF_PACKET = 4

class Checked_addresses():
    def __init__(self, serv: list) -> None:
        self.domain = serv[0]
        self.date = []
        self.ip_address = []
        self.packet_loss = []
        self.rtt = []
        self.port = []
        self.port_status = []

        for i in serv[1]:
            # ICMP 
            if serv[2] == []:
                self.date.append(datetime.datetime.now().isoformat().replace("T", " "))
                self.rtt.append(ping(i, count=COUNT_OF_PACKET, timeout=TIMEOUT_PING).rtt_avg_ms)
                self.ip_address.append(i)
                self.packet_loss.append(ping(i, count=COUNT_OF_PACKET, timeout=TIMEOUT_PING).packet_loss)
                self.port.append(-1)
                self.port_status.append("Ports are missing")
                continue

            # Other
            for j in serv[2]:
                res = check_adr(i, int(j))

                self.date.append(datetime.datetime.now().isoformat().replace("T", " "))
                self.rtt.append(res[0])
                self.ip_address.append(i)
                self.packet_loss.append(res[1])
                self.port.append(j)
                self.port_status.append(res[2])

    def show(self):
        for i in range(len(self.ip_address)):
            result = self.date[i]
            result += ' | ' + self.domain
            result += ' | ' + self.ip_address[i]
            result += ' | ' + str(self.packet_loss[i])
            result += ' | ' + str(self.rtt[i]) + ' ms'
            result += ' | ' + str(self.port[i])
            result += ' | ' + str(self.port_status[i])
            print(f"{result}")
        print()

def make_adr_from_row(row: list) -> list:
    # Преобразование в формат ['доменное имя', ['IP-адреса'], ['порты']] или ['???', ['IP-адрес'], False]
    if "." in row[0] or row[0] == 'localhost':
        if not (row[0].replace(".", "", len(row[0]))).isdigit():
            row.insert(1, get_domain_adr(row[0]))
        else:
            try:
                row.insert(0, socket.gethostbyaddr(row[0]))
                row[1] = [row[1]]
            except:
                row.insert(0, "Address hasn't hostname")
                row[1] = [row[1]]
        if (row[2].replace(",", "", len(row[2]))).isdigit():
            row[2] = row[2].split(",")
        else:
            row[2] = []
    else:
        return

def check_adr(address: str, port: int) -> tuple:
    sock = socket.socket(AF_INET, SOCK_STREAM)
    sock.settimeout(TIMEOUT_SOCKET)
    a = ping(address, timeout=TIMEOUT_PING, count=COUNT_OF_PACKET)
    rtt = a.rtt_avg_ms
    packet_loss = a.packet_loss
    
    try:
        sock.connect((address, port))
        return(rtt, float(packet_loss), "Opened")
    except:

        return (rtt, float(packet_loss), "Not opened")


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
            row_of_addresses = Checked_addresses(row)
            row_of_addresses.show()
