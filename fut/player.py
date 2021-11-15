import time
import json
import numpy as np
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError
from typing import Union

from .utils import parse_html_table, years_since, create_url


class Player:
    def __init__(self, pid: int, game: int, rid=None) -> None:
        """
        Player base class with methods to download player attributes and
        price information.

        :pid: Unique player id.
        :game: Fifa version.
        :rid, optional: Unique player resource id, used for fetching prices.
        """
        self.game = game
        self.pid = pid
        self.rid = rid
        self.name = None
        self.url = create_url(game, pid, prices=False)
        self.url_prices = create_url(game, rid, True) if rid else None

    def __str__(self) -> str:
        return self.name if self.name else str(self.pid)

    def __eq__(self, other):
        if type(other) == int:
            identifier = self.pid
        elif type(other) == str:
            identifier = self.name
        else:
            identifier = self.name if self.name else str(self.pid)
        return identifier == other

    def _download_soup(
        self, soup_type: str, proxy: Union[str, None] = None
    ) -> BeautifulSoup:
        """
        Download the parsed soup for the player or their prices.

        :soup_type: one of ('attributes', 'prices')
        """
        proxies = {"http": proxy, "https": proxy} if proxy else {}
        url = self.url_prices if soup_type == "prices" else self.url

        resp = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(resp.text, features="lxml")
        if "does not have permission" in soup.text:
            time.sleep(2)
            raise ProxyError

        return soup

    def download(self, proxy: Union[str, None] = None) -> None:
        """
        Download the player's information, attributes and statistics.
        """
        soup = self._download_soup("attributes", proxy=proxy)

        if "We're sorry" in soup.text:
            return

        self.rid = int(soup.find("div", {"id": "page-info"})["data-player-resource"])

        self.information = self._parse_information(soup)
        self.url_prices = create_url(self.game, self.rid, True)

        # Attributes
        stats = json.loads(soup.find("div", {"id": "player_stats_json"}).text.strip())[0]
        self.attributes = self._parse_attributes(stats)

    def download_prices(self, proxy: Union[str, None] = None) -> list:
        """
        Download the player's daily prices.
        """
        soup = self._download_soup("prices", proxy)
        soup_dict = json.loads(soup.text)
        if "ps" not in soup_dict:
            return []

        return [
            (time.strftime("%Y-%m-%d", time.gmtime(epoch // 1000)), price)
            for epoch, price in json.loads(soup.text)["ps"]
        ]

    def _parse_information(self, soup: BeautifulSoup) -> dict:
        """
        Extract the player's information.

        There's some oddities depending on the game - for example FIFA 19 data was
        missing international reputation for all icons (bar moments) and there was
        no body type data for any players.

        Args:
            soup: BeautifulSoup of the player's futbin page.
        """
        info_table = soup.find("table", {"class": "table table-info"})
        info = parse_html_table(info_table)

        # Add padding to match structure of info list.
        if "Career" not in info[0]:
            info = [""] + info
        if self.game <= 19 and len(info) == 19:
            info = info[:7] + [3] + info[7:]

        age_f = info[17] if self.game <= 19 else info[18]

        pgp_stats = [
            stat.text.split()[-1].replace("-", "0")
            for stat in soup.findAll("div", {"class": "ps4-pgp-data"})[-3:]
        ]

        return {
            "name": info[1],
            "rating": int(soup.find("div", {"class": "pcdisplay-rat"}).text),
            "position": soup.find("div", {"id": "page-info"})["data-position"],
            "club": info[2],
            "nation": info[3],
            "league": info[4],
            "skill_moves": int(info[5]),
            "weak_foot": int(info[6]),
            "reputation": int(info[7]),
            "foot": info[8],
            "height": int(info[9].split("cm")[0]),
            "weight": int(info[10]),
            "revision": info[11],
            "defensive_wr": info[12],
            "attacking_wr": info[13],
            "added_date": datetime.strptime(info[14], "%Y-%m-%d"),
            "origin": info[15],
            "body_type": info[17] if self.game > 19 else None,
            "age": int(age_f.split(" ")[0]) if "years" in age_f else years_since(age_f),
            "num_games": int(pgp_stats[2].replace(",", "")),
            "num_goals": float(pgp_stats[1]),
            "num_assists": float(pgp_stats[0]),
        }

    def _parse_attributes(self, stats: dict) -> dict:
        """
        Extract the individual player attributes

        :stats: dictionary containing the player statistics.
        :position: player's position.
        """
        return {
            stats_["id"]: stats_["value"]
            for stats_ in np.concatenate(list(stats.values()))
        }
