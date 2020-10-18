import os
import logging
import subprocess
from datetime import datetime


def setup_logger(log) -> None:
    logging.basicConfig(
        filename=f"logs/{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.log",
        filemode="w",
        level=getattr(logging, log.upper()),
        datefmt="%H:%M:%S",
        format="%(asctime)s - %(levelname)s: %(message)s",
    )


def parse_html_table(table) -> list:
    data = []
    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        data.append("".join([ele for ele in cols if ele]))
    return data


def years_since(date: str) -> int:
    """Number of years between argument and current date"""
    delta = datetime.now() - datetime.strptime(date, "%d-%m-%Y")
    return int(delta.days / 365)


class NordVPN:
    def __init__(self):
        return

    @staticmethod
    def disconnect() -> int:
        return os.system("nordvpn d")

    @staticmethod
    def connect() -> int:
        return os.system("nordvpn connect us")

    @staticmethod
    def reconnect() -> int:
        a = os.system("nordvpn d")
        b = os.system("nordvpn connect us")
        return a * b

    @staticmethod
    def status() -> tuple:
        vpn_status = str(subprocess.check_output(["nordvpn", "status"]))
        if "Disconnected" in vpn_status:
            return (False, 0)
        else:
            vpn_status = vpn_status.split("Uptime:")[-1]
            time_active = vpn_status.strip(r"\'\n seconds")
            if "minutes" in time_active:
                mins, secs = time_active.split(" minutes ")
            elif "minute" in time_active:
                mins, secs = time_active.split(" minute ")
            else:
                mins = 0
                secs = time_active
            return (True, (int(mins) * 60) + int(secs))
