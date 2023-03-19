from config import TIMEOUT_PING, OPENED, NOT_OPENED, \
    TIMEOUT_SOCKET, COUNT_OF_PACKET, \
    MISSING_PORTS, NOT_INTERNET_CONNECTION, ADDRESS_ERROR
from pythonping import ping
from socket import AF_INET, SOCK_STREAM

import datetime
import asyncio
import socket


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

        self.loop = asyncio.get_event_loop()

        for address in host_row[1]:
            self.loop.run_until_complete(self.fill_data(host_row[2], address))
            

    async def fill_data(self, ports: list, address: str) -> None:
        """Method runs methods for filling data depending on ports.
        Args:
            ports: list - list of ports.
            address: str - host address.
        """
        if not ports:
            self.add_date()
            await self.pinging(address)
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

    async def pinging(self, address: str) -> None:
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