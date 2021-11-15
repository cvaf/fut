import os
import ray
import pickle
import requests
from bs4 import BeautifulSoup
from requests.exceptions import SSLError, ProxyError

from .player import Player
from .constants import DATA_FOLDER, MAX_PIDS


@ray.remote
class Scraper:
    def __init__(self, game: int) -> None:
        """
        Web scraper base class.

        :game: fifa version
        """
        self.game = game
        self.players = []

    def lookup(self, identifier: int) -> Player:
        player = [p for p in self.players if p == identifier]
        return player[0] if player else None

    def update(self, storage, proxy_handler):
        while not ray.get(storage.get_terminate_status.remote()):
            pid = ray.get(storage.get_pending_pid.remote())
            player = Player(pid, self.game)
            proxy = ray.get(proxy_handler.get_proxy.remote())

            while not player.updated:
                try:
                    player.download(proxy)
                    player.download_prices(proxy)
                except (SSLError, ProxyError):
                    proxy = ray.get(proxy_handler.refresh_proxy.remote(proxy))

            storage.add_player.remote(player)


@ray.remote
class SharedStorage:
    def __init__(self, game: int) -> None:
        self.game = game
        self.pending_pids = list(range(self._latest_pid()))
        self.players = []
        self.file_path = os.path.join(DATA_FOLDER, f"players{game}.pkl")
        if os.path.isfile(self.file_path):
            self._load()
        self.terminate = False

    def _latest_pid(self) -> int:
        """
        Find the latest available player ID on futbin
        """
        if self.game == 22:
            resp = requests.get("https://www.futbin.com/latest")
            soup = BeautifulSoup(resp.text, "lxml")
            pid = soup.find_all("table")[0].find("a").attrs["href"].split("/")[3]
        elif self.game in MAX_PIDS.keys():
            pid = MAX_PIDS.get(self.game)
        else:
            raise ValueError(f"Game value: {self.game} is not supported.")
        return int(pid)

    def _load(self) -> None:
        with open(self.file_path, "rb") as f:
            players = pickle.load(f)
        self.players.extend(players)
        current_pid = max([player.pid for player in self.players]) if self.players else 0
        self.pending_pids = list(range(current_pid, max(self.pending_pids)))

    def save(self) -> None:
        with open(self.file_path, "wb") as f:
            pickle.dump(self.players, f, pickle.HIGHEST_PROTOCOL)

    def get_pending_pid(self) -> int:
        pid = self.pending_pids[0]
        self.pending_pids.pop(0)
        if not self.pending_pids:
            self.terminate = True
        return pid

    def get_pending(self) -> list:
        return self.pending_pids

    def get_terminate_status(self) -> bool:
        return self.terminate

    def terminate(self) -> None:
        self.terminate = True
