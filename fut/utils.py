import logging
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def setup_logger(log) -> None:
    logging.basicConfig(
        filename=f"logs/{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.log",
        filemode="w",
        level=getattr(logging, log.upper()),
        datefmt="%H:%M:%S",
        format="%(asctime)s - %(levelname)s: %(message)s",
    )


def parse_html_table(table, concat=True) -> list:
    data = []
    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        if concat:
            entries = "".join([ele for ele in cols if ele])
        else:
            entries = [ele for ele in cols if ele]

        data.append(entries)
    return data


def years_since(date: str) -> int:
    """Number of years between argument and current date"""
    delta = datetime.now() - datetime.strptime(date, "%d-%m-%Y")
    return int(delta.days / 365)


class ProxyHandler:
    URL = "https://www.us-proxy.org"
    PROXY_TYPES = ["anonymous", "elite proxy"]

    def __init__(self) -> None:
        self.proxies = []
        self.blacklist_proxies = []
        self._new_proxies()

    def _new_proxies(self) -> None:
        resp = requests.get(self.URL)
        soup = BeautifulSoup(resp.text, "lxml")
        parsed_table = parse_html_table(soup.find("tbody"), concat=False)
        proxies = [
            proxy[0] + ":" + proxy[1]
            for proxy in parsed_table
            if proxy[2] == "US" and proxy[4] in self.PROXY_TYPES
        ]
        self.proxies = [proxy for proxy in proxies if proxy not in self.blacklist_proxies]

    def remove_proxy(self, proxy: str) -> None:
        if proxy in self.proxies:
            self.proxies.remove(proxy)
        self.blacklist_proxies.append(proxy)

    def sample_proxy(self) -> str:
        if not self.proxies:
            self._new_proxies()
        return random.choice(self.proxies)
