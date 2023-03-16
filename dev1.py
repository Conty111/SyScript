import csv
import socket
from pythonping import ping
from socket import AF_INET, SOCK_STREAM



sock = socket.socket(AF_INET, SOCK_STREAM)

def make_adr(adr: str):
    try:
        return socket.gethostbyname_ex(adr)[2]
    except:
        return "Error in domain adress"

def check_adr(serv: list):
    result = []
    print(serv)
    for i in serv[1]:
        if serv[2] == False:
            # ICMP
            result.append(ping(i, count=4, timeout=5))
            continue

        for j in serv[2]:
            result.append(sock.connect_ex((i, int(j))))
            print(i, j)
            sock.connect_ex((i, int(j)))

    return result




with open("test.csv", newline='') as csvfile:
    file_input = csv.reader(csvfile, delimiter=";")
    for row in file_input:

        # Преобразование в формат ['доменное имя', ['IP-адреса'], ['порты']] или ['???', ['IP-адрес'], False]
        if row[0] and "." in row[0] or row[0] == 'localhost':
            if not (row[0].replace(".", "", len(row[0]))).isdigit():
                row.insert(1, make_adr(row[0]))
            else:
                try:
                    row.insert(0, socket.gethostbyaddr(row[0]))
                    row[1] = [row[1]]
                except:
                    row.insert(0, "???")
                    row[1] = [row[1]]
            if (row[2].replace(",", "", len(row[2]))).isdigit():
                row[2] = row[2].split(",")
            else:
                row[2] = False
        else:
            continue
        
        print(check_adr(row))
