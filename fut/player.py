import time
import json
import numpy as np
from datetime import datetime

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from requests.exceptions import ProxyError  # type: ignore
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
        self.attributes = dict(game=game, pid=pid, update_date=None)
        self.game = game
        self.pid = pid
        self.rid = rid
        self.url = create_url(game, pid, prices=False)
        self.url_prices = create_url(game, rid, True) if rid else None
        self.updated = False

    def __eq__(self, other: Union[object, int, str]) -> bool:
        identifier = self.attributes.get("name") if isinstance(other, str) else self.pid
        return identifier == other

    def _download_soup(self, soup_type: str) -> BeautifulSoup:
        """
        Download the parsed soup for the player or their prices.

        :soup_type: one of ('attributes', 'prices')
        """
        url = self.url_prices if soup_type == "prices" else self.url

        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, features="lxml")
        if "does not have permission" in soup.text:
            time.sleep(2)
            raise ProxyError

        return soup

    def download(self) -> dict:
        """
        Download the player's information, attributes and statistics.
        """
        soup = self._download_soup("attributes")

        if "We're sorry" in soup.text:
            self.updated = True
            return {}

        self.rid = self.attributes["rid"] = int(
            soup.find("div", {"id": "page-info"})["data-player-resource"]
        )
        self.attributes.update(
            {
                "rating": int(soup.find("div", {"class": "pcdisplay-rat"}).text),
                "position": soup.find("div", {"id": "page-info"})["data-position"],
            }
        )

        information = parse_html_table(soup.find("table", {"class": "table table-info"}))
        self.attributes.update(information)
        self.url_prices = create_url(self.game, self.rid, True)

        # PGP Stats
        pgp_stats = [
            stat.text.split()[-1].replace("-", "0")
            for stat in soup.findAll("div", {"class": "ps4-pgp-data"})[-3:]
        ]
        self.attributes.update(
            {
                "num_games": int(pgp_stats[2].replace(",", "")),
                "num_goals": float(pgp_stats[1]),  # type: ignore
                "num_assists": float(pgp_stats[0]),  # type: ignore
            }
        )

        # Attributes
        table = json.loads(soup.find("div", {"id": "player_stats_json"}).text.strip())[0]
        _attributes = {s["id"]: s["value"] for s in np.concatenate(list(table.values()))}
        self.attributes.update(_attributes)

        self.attributes["update_date"] = datetime.now()  # type: ignore
        self.updated = True
        return self.attributes

    def download_prices(self) -> list:
        """
        Download the player's daily prices.
        """
        soup = self._download_soup("prices")
        soup_dict = json.loads(soup.text)
        if "ps" not in soup_dict:
            return []

        self.prices = [
            (time.strftime("%Y-%m-%d", time.gmtime(epoch // 1000)), price)
            for epoch, price in json.loads(soup.text)["ps"]
        ]

        return self.prices
