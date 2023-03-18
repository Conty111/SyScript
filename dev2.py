"""Main file for project."""
from config import TIMEOUT_PING, DOMAIN_ERROR, OPENED, NOT_OPENED, \
    NOT_HOSTNAME, FILE_TO_READ, TIMEOUT_SOCKET, COUNT_OF_PACKET, \
    MISSING_PORTS, NOT_INTERNET_CONNECTION

from socket import AF_INET, SOCK_STREAM
from pythonping import ping

import datetime
import socket
import csv


class CheckAddresses:
    """Class for collecting information about hosts."""

    def __init__(self, host_row: list) -> None:
        """Initialise method for getting info from host.
        Args:
            host_row: list - list of parameters for analysis.
        """
        self.domain = host_row[0]
        self.date = []
        self.ip_address = []
        self.packet_loss = []
        self.rtt = []
        self.port = []
        self.port_status = []

        for address in host_row[1]:
            self.fill_data(host_row[2], address)

    def fill_data(self, ports: list, address: str) -> None:
        """Method runs methods for filling data depending on ports.
        Args:
            ports: list - list of ports.
            address: str - host address.
        """
        if not ports:
            self.add_date()
            self.pinging(address)
            self.missing_port()
            self.ip_address.append(address)
            return

        for port in ports:
            self.add_characteristics(address, int(port))
            self.ip_address.append(address)
            self.port.append(port)
            self.add_date()

    def missing_port(self) -> None:
        """Method runs if ports list is empty."""
        self.port.append(-1)
        self.port_status.append(MISSING_PORTS)

    def pinging(self, address: str) -> None:
        """Method uses ping function and saves data from response.
        Args:
            address: str - host address.
        """
        try:
            ping_adr = ping(address, count=COUNT_OF_PACKET, timeout=TIMEOUT_PING)
            self.rtt.append(ping_adr.rtt_avg_ms)
            self.packet_loss.append(ping_adr.packet_loss * COUNT_OF_PACKET)
        except BaseException:
            print(NOT_INTERNET_CONNECTION)
            exit()
        

    def add_date(self) -> None:
        """Method adds date if it runs."""
        now_date = datetime.datetime.now().isoformat().replace("T", " ")
        self.date.append(now_date)

    def add_characteristics(self, address: str, port: int) -> None:
        """Method gets rtt, packet_loss and port status.
        Args:
            address: str - host address.
            port: int - port for check.
        """
        characteristics = self.get_socket_characteristics(address, port)
        self.rtt.append(characteristics[0])
        self.packet_loss.append(characteristics[1])
        self.port_status.append(characteristics[2])

    def show(self):
        """Method prints all collected data in readable form."""
        for num, _ in enumerate(self.ip_address):
            all_info = [self.date[num],
                        self.domain,
                        self.ip_address[num],
                        str(self.packet_loss[num]),
                        f"{str(self.rtt[num])} ms",
                        str(self.port[num]),
                        str(self.port_status[num]),
                        ]
            print(" | ".join(all_info))
        print("\n")

    @staticmethod
    def get_socket_characteristics(address: str, port: int) -> tuple:
        """Method tries to connect by socket and get sockets parameters.
        Args:
            address: str - host address.
            port: int - port for connection.
        """
        ping_adr = ping(address, timeout=TIMEOUT_PING, count=COUNT_OF_PACKET)
        rtt = ping_adr.rtt_avg_ms
        packet_loss = ping_adr.packet_loss * COUNT_OF_PACKET
        sock = socket.socket(AF_INET, SOCK_STREAM)
        sock.settimeout(TIMEOUT_SOCKET)
        try:
            sock.connect((address, port))
        except BaseException:
            return rtt, float(packet_loss), NOT_OPENED
        return rtt, float(packet_loss), OPENED


def make_adr_from_row(cur_row: list) -> list:
    """Method refactors row into ["domain name", ["ip"], ["ports"]].
    Args:
        cur_row: list - row for format check.
    """
    if "." in cur_row[0] or cur_row[0] == "localhost":
        if (cur_row[0].replace(".", "", len(cur_row[0]))).isdigit():
            try:
                cur_row.insert(0, socket.gethostbyaddr(cur_row[0]))
            except BaseException:
                cur_row.insert(0, NOT_HOSTNAME)
            cur_row[1] = [cur_row[1]]
        else:
            cur_row.insert(1, get_domain_adr(cur_row[0]))

        if (cur_row[2].replace(",", "", len(cur_row[2]))).isdigit():
            cur_row[2] = cur_row[2].split(",")
        else:
            cur_row[2] = []
        return cur_row


def get_domain_adr(adr: str) -> str:
    """Function tries to get socket host.
    Args:
        adr: str - host address.
    Returns:
        str - domain name or error.
    """
    try:
        return socket.gethostbyname_ex(adr)[2]
    except BaseException:
        return DOMAIN_ERROR


if __name__ == "__main__":
    sock = socket.socket(AF_INET, SOCK_STREAM)
    with open(FILE_TO_READ, newline="") as csvfile:
        for row in csv.reader(csvfile, delimiter=";"):
            if row:
                formed_row = make_adr_from_row(row)
                if formed_row:
                    row_of_addresses = CheckAddresses(formed_row)
                    row_of_addresses.show()
                    close = input("Press any key to close...")
