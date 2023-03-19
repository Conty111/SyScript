"""Main file for project."""
from config import DOMAIN_ERROR, NOT_HOSTNAME, FILE_TO_READ
from CheckAddresses import CheckAddresses
from socket import AF_INET, SOCK_STREAM

import socket
import csv


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