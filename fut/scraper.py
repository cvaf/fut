import pickle
import logging
import requests
from bs4 import BeautifulSoup

from multiprocessing import Pool
from tqdm import tqdm

from .player import Player


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

    def __str__(self) -> int:
        return self.game

    def lookup(self, identifier):
        player = [p for p in self.players if p == identifier]
        if player:
            return player[0]
        else:
            return None

    def save(self) -> None:
        """
        Save a pickle of this instance at data/scraper{game}.pkl where
        game is this instance's game version.
        """
        logging.debug(f"Saving {self.game} scraper instance.")
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
        if self.game == 20:
            pid = 50966
        elif self.game == 19:
            pid = 21437
        else:
            resp = requests.get("https://www.futbin.com/latest")
            soup = BeautifulSoup(resp.text, "lxml")
            pid = soup.find_all("table")[0].find("a").attrs["href"].split("/")[3]
        return int(pid)

    def update_players(self, num_processes=12) -> None:
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

        # break up the updates in increments
        num_players = len(new_players)
        with Pool(num_processes) as p:
            updated_players = list(
                tqdm(p.imap(update_player, new_players), total=num_players)
            )
        self.players.extend(updated_players)
        self.save()

    def update_prices(self, num_processes=8) -> None:
        """
        Downloads the prices for all the players in the players array.

        :num_processes: number of multiprocessing workers to use.
        """

        with Pool(num_processes) as p:
            updated_players = list(
                tqdm(p.imap(update_prices, self.players), total=len(self.players))
            )

        logging.info("Done updating.")
        self.players = updated_players
