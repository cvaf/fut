from bs4 import BeautifulSoup  # type: ignore
from datetime import datetime

from typing import List


def _clean_string(text: str, key: bool = False) -> str:
    text = text.replace('\n','').replace('\r','').lstrip().rstrip()
    return text if not key else text.lower().replace(".", "").replace(" ", "_")


def parse_html_table(table: BeautifulSoup) -> dict:
    output = {}
    for row in table.find_all("tr"):
        k, d = row.find("th"), row.find("td")
        if k and d:
            output[_clean_string(k.text, key=True)] = _clean_string(d.text)

    return output


def years_since(date: str) -> int:
    """Number of years between argument and current date"""
    delta = datetime.now() - datetime.strptime(date, "%d-%m-%Y")
    return int(delta.days / 365)


def create_url(game: int, idd: int, prices: bool = False) -> str:
    BASE_URL = "https://www.futbin.com"
    if prices:
        return f"{BASE_URL}/{game}/playerGraph?type=daily_graph&year={game}&player={idd}"
    else:
        return f"{BASE_URL}/{game}/player/{idd}"
