import logging

import json
import pickle
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from multiprocessing import Pool
from tqdm import tqdm

from .utils import parse_html_table, years_since
from .constants import base_url


def update_player(player):
    player.download()
    return player


def update_prices(player):
    player.download_prices()
    return player


class Scraper:
    def __init__(self, game: int) -> None:
        """
        Web scraper base class.

        :game: fifa version
        """
        self.game = game
        self.players = []

    def __str__(self):
        return self.game

    def save(self) -> None:
        """
        Save a pickle of this instance at data/scraper{game}.pkl where
        game is this instance's game version.
        """
        with open(f"data/scraper{self.game}.pkl", "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(game):
        with open(f"data/scraper{game}.pkl", "rb") as f:
            return pickle.load(f)

    def _latest_pid(self) -> int:
        """
        Find the latest available player ID on futbin
        """
        # TODO: Adjust this to accommodate other fifa versions
        resp = requests.get("https://www.futbin.com/latest")
        soup = BeautifulSoup(resp.text, "lxml")
        pid = soup.find_all("table")[0].find("a").attrs["href"].split("/")[3]
        return int(pid)

    def update_players(self, num_processes=8) -> None:
        """
        Updates the players array by fetching newly added players and their
        attributes.

        :num_processes: number of multiprocessing workers to use.
        """

        current_pid = max([player.pid for player in self.players]) if self.players else 0
        latest_pid = self._latest_pid()

        new_players = [
            Player(pid, self.game) for pid in range(current_pid + 1, latest_pid + 1)
        ]

        with Pool(num_processes) as p:
            new_players = list(
                tqdm(p.imap(update_player, new_players), total=len(new_players))
            )

        self.players.extend(new_players)

    def update_prices(self, num_processes=8) -> None:
        """
        Downloads the prices for all the players in the players array.

        :num_processes: number of multiprocessing workers to use.
        """

        with Pool(num_processes) as p:
            updated_players = list(
                tqdm(p.imap(update_prices, self.players), total=len(self.players))
            )

        self.players = updated_players


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

    def __str__(self):
        return self.name if self.name else str(self.pid)

    def _download_soup(self, soup_type) -> BeautifulSoup:
        """
        Download the parsed soup for the player or their prices.

        :soup_type: one of ('attributes', 'prices')
        """

        if soup_type == "attributes":
            url = f"{base_url}/{self.game}/player/{self.pid}"
        elif soup_type == "prices":
            url = (
                f"{base_url}/{self.game}/playerGraph?"
                f"type=daily_graph&year={self.game}&player={self.rid}"
            )
        else:
            raise ValueError("soup_type must be attributes or prices.")

        # TODO: Add exception handling here
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, features="lxml")

        if "does not have permission" in soup.text:
            logging.debug("Access interrupted.")
            proceed = input("Proceed?")
            if proceed:
                soup = self.download_soup(soup_type)

        return soup, resp

    def download(self) -> None:
        """
        Download the player's information, attributes and statistics.
        """
        try:
            soup, resp = self._download_soup("attributes")
            self.rid = int(soup.find("div", {"id": "page-info"})["data-player-resource"])
        except Exception as e:
            logging.error(f"Failed downloading soup for {self.pid}; {str(e)}")
            return

        # Player information
        info_table = soup.find("table", {"class": "table table-info"})
        info = parse_html_table(info_table)
        if info[6] in {"Right", "Left"}:
            return
        self.name = info[0]
        self.club = info[1]
        self.nation = info[2]
        self.league = info[3]
        self.skill_moves = int(info[4])
        self.weak_foot = int(info[5])
        self.reputation = int(info[6])
        self.foot = info[7]
        self.height = int(info[8].split("cm")[0])
        self.weight = int(info[9])
        self.revision = info[10]
        self.defensive_wr = info[11]
        self.attacking_wr = info[12]
        self.added_date = datetime.strptime(info[13], "%Y-%m-%d")
        self.origin = info[14]
        if "years" in info[17]:
            self.age = int(info[17].split(" ")[0])
        else:
            self.age = years_since(info[17])
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
        self._parse_attributes(stats, self.position)

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

    def _parse_attributes(self, stats, position) -> None:
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
            self.acceleration = extract_stat(speed_stats, 1)
            self.sprint_speed = extract_stat(speed_stats, 2)

            positioning_stats = stats["gkpositioning"]
            self.positioning = extract_stat(positioning_stats, 0)
