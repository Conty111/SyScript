import csv
import socket
from pythonping import ping


def make_adr(adr: str):
    try:
        return socket.gethostbyname_ex(adr)[2]
    except:
        return "Error in domain adress"

# def check_adr(serv: list):
#     for i in serv[1]:
#         if serv[2]:
#             # ICMP
#             print("NOne")
#             ping(i, count=4, timeout=5, verbose=True)
#         # for j in serv[2]:
            
#         #     else:
#         #         socket




with open("test.csv", newline='') as csvfile:
    file_input = csv.reader(csvfile, delimiter=";")
    for row in file_input:

        # Преобразование в формат ['доменное имя', ['IP-адреса'], ['порты']]
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
            row[2] = row[2].split(",")
        else:
            continue
        # check_adr(row)
            