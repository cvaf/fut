import time
import json
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.exceptions import SSLError, ProxyError

from .utils import parse_html_table, years_since, ProxyHandler
from .constants import BASE_URL

proxy_handler = ProxyHandler()


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

    def _download_soup(self, soup_type) -> BeautifulSoup:
        """
        Download the parsed soup for the player or their prices.

        :soup_type: one of ('attributes', 'prices')
        """

        if soup_type == "attributes":
            url = f"{BASE_URL}/{self.game}/player/{self.pid}"
        elif soup_type == "prices":
            url = (
                f"{BASE_URL}/{self.game}/playerGraph?"
                f"type=daily_graph&year={self.game}&player={self.rid}"
            )
        else:
            raise ValueError("soup_type must be attributes or prices.")

        proxy = proxy_handler.sample_proxy()
        try:
            resp = requests.get(url, proxies={"http": proxy, "https": proxy})
            soup = BeautifulSoup(resp.text, features="lxml")
            error = False
        except (SSLError, ProxyError):
            error = True

        if error or "does not have permission" in soup.text:
            logging.info("Access interrupted.")
            proxy_handler.remove_proxy(proxy)
            time.sleep(2)
            soup, resp = self._download_soup(soup_type)

        return soup, resp

    def download(self) -> None:
        """
        Download the player's information, attributes and statistics.
        """
        soup, resp = self._download_soup("attributes")

        if "We're sorry" in soup.text:
            return

        try:
            self.rid = int(soup.find("div", {"id": "page-info"})["data-player-resource"])
            self._parse_information(soup)
        except Exception as e:
            logging.error(f"Failed parsing information for {self.pid}; {str(e)}")
            return
        self.rating = int(soup.find("div", {"class": "pcdisplay-rat"}).text)
        self.position = soup.find("div", {"id": "page-info"})["data-position"]

        # PGP information
        pgp_div = soup.findAll("div", {"class": "ps4-pgp-data"})
        pgp_stats = [stat.text.split()[-1].replace("-", "0") for stat in pgp_div[-3:]]
        self.assists = float(pgp_stats[0])
        self.goals = float(pgp_stats[1])
        self.num_games = int(pgp_stats[2].replace(",", ""))

        # Attributes
        stats = json.loads(soup.find("div", {"id": "player_stats_json"}).text.strip())[0]
        try:
            self._parse_attributes(stats, self.position)
        except Exception as e:
            logging.error(f"Failed parsing attributes for {self.pid}; {str(e)}")

    def download_prices(self) -> None:
        """
        Download the player's daily prices.
        """

        self.prices = []
        soup, resp = self._download_soup("prices")
        soup_dict = json.loads(soup.text)
        if "ps" not in soup_dict:
            return
        for epoch, price in json.loads(soup.text)["ps"]:
            self.prices.append(
                (time.strftime("%Y-%m-%d", time.gmtime(epoch // 1000)), price)
            )

    def _parse_information(self, soup: BeautifulSoup) -> None:
        """
        Extract the player's information.
        There's some oddities depending on the game - for example FIFA 19 data was
        missing international reputation for all icons (bar moments) and there was
        no body type data for any players.

        :soup: BeautifulSoup of the player's futbin page.
        """
        info_table = soup.find("table", {"class": "table table-info"})
        info = parse_html_table(info_table)

        self.name = info[0]
        self.club = info[1]
        self.nation = info[2]
        self.league = info[3]
        self.skill_moves = int(info[4])
        self.weak_foot = int(info[5])

        # The reputation field
        shift = 0
        if info[6] in {"Right", "Left"}:
            shift = 1
        self.reputation = int(info[6]) if shift == 0 else 4
        self.foot = info[7 - shift]
        self.height = int(info[8 - shift].split("cm")[0])
        self.weight = int(info[9 - shift])
        self.revision = info[10 - shift]
        self.defensive_wr = info[11 - shift]
        self.attacking_wr = info[12 - shift]
        self.added_date = datetime.strptime(info[13 - shift], "%Y-%m-%d")
        self.origin = info[14 - shift]
        if "years" in info[-1]:
            self.age = int(info[-1].split(" ")[0])
        else:
            self.age = years_since(info[-1])

    def _parse_attributes(self, stats: dict, position: str) -> None:
        """
        Extract the individual player attributes

        :stats: dictionary containing the player statistics.
        :position: player's position.
        """

        def extract_stat(s, i):
            return int(s[i]["value"])

        if position != "GK":

            pace_stats = stats["pace"]
            self.pace = extract_stat(pace_stats, 0)
            self.acceleration = extract_stat(pace_stats, 1)
            self.sprint_speed = extract_stat(pace_stats, 2)

            shooting_stats = stats["shooting"]
            self.shooting = extract_stat(shooting_stats, 0)
            self.positioning = extract_stat(shooting_stats, 1)
            self.finishing = extract_stat(shooting_stats, 2)
            self.shot_power = extract_stat(shooting_stats, 3)
            self.long_shots = extract_stat(shooting_stats, 4)
            self.volleys = extract_stat(shooting_stats, 5)
            self.penalties = extract_stat(shooting_stats, 6)

            passing_stats = stats["passing"]
            self.passing = extract_stat(passing_stats, 0)
            self.vision = extract_stat(passing_stats, 1)
            self.crossing = extract_stat(passing_stats, 2)
            self.fk_accuracy = extract_stat(passing_stats, 3)
            self.short_passing = extract_stat(passing_stats, 4)
            self.long_passing = extract_stat(passing_stats, 5)
            self.curve = extract_stat(passing_stats, 6)

            dribbling_stats = stats["dribbling"]
            self.dribbling = extract_stat(dribbling_stats, 0)
            self.agility = extract_stat(dribbling_stats, 1)
            self.balance = extract_stat(dribbling_stats, 2)
            self.reactions = extract_stat(dribbling_stats, 3)
            self.ball_control = extract_stat(dribbling_stats, 4)
            self.dribble = extract_stat(dribbling_stats, 5)
            self.composure = extract_stat(dribbling_stats, 6)

            defending_stats = stats["defending"]
            self.defending = extract_stat(defending_stats, 0)
            self.interceptions = extract_stat(defending_stats, 1)
            self.heading_accuracy = extract_stat(defending_stats, 2)
            self.def_awareness = extract_stat(defending_stats, 3)
            self.standing_tackle = extract_stat(defending_stats, 4)
            self.sliding_tackle = extract_stat(defending_stats, 5)

            physicality_stats = stats["physical"]
            self.physicality = extract_stat(physicality_stats, 0)
            self.jumping = extract_stat(physicality_stats, 1)
            self.stamina = extract_stat(physicality_stats, 2)
            self.strength = extract_stat(physicality_stats, 3)
            self.aggression = extract_stat(physicality_stats, 4)

        else:

            diving_stats = stats["gkdiving"]
            self.diving = extract_stat(diving_stats, 0)

            handling_stats = stats["gkhandling"]
            self.handling = extract_stat(handling_stats, 0)

            kicking_stats = stats["gkkicking"]
            self.kicking = extract_stat(kicking_stats, 0)

            reflexes_stats = stats["gkreflexes"]
            self.reflexes = extract_stat(reflexes_stats, 0)

            speed_stats = stats["speed"]
            speed = extract_stat(speed_stats, 0)
            self.acceleration = speed
            self.sprint_speed = speed

            positioning_stats = stats["gkpositioning"]
            self.positioning = extract_stat(positioning_stats, 0)
