import os
import ray
import pickle
import requests  # type: ignore
import pandas as pd  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from requests.exceptions import SSLError, ProxyError  # type: ignore
from typing import List, Union

from .player import Player
from .constants import DATA_FOLDER, MAX_PIDS, HEADERS


@ray.remote
class SharedStorage:
    def __init__(self, game: int) -> None:
        self.game = game
        self.pending_pids = list(range(self._latest_pid()))
        self.players: List[Player] = []
        self.file_path = os.path.join(DATA_FOLDER, f"players{game}.pkl")
        if os.path.isfile(self.file_path):
            self._load()
        self.is_terminated = False

    def _latest_pid(self) -> int:
        """
        Find the latest available player ID on futbin
        """
        if self.game == 22:
            resp = requests.get("https://www.futbin.com/latest", headers=HEADERS)
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
        current_pid = max([player.pid for player in self.players]) if self.players else 0  # type: ignore
        self.pending_pids = list(range(current_pid, max(self.pending_pids)))

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def save_pickle(self) -> None:
        with open(self.file_path, "wb") as f:
            f.write(pickle.dumps(self.players))

    def attributes_to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([player.attributes for player in self.players])

    def prices_to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            [(player.pid, *price) for player in self.players for price in player.prices],
            columns=["pid", "date", "price"],
        )

    def get_pending_pid(self) -> int:
        pid = self.pending_pids[0]
        self.pending_pids.pop(0)
        if not self.pending_pids:
            self.is_terminated = True
        return pid

    def get_pending(self) -> list:
        return self.pending_pids

    def get_terminate_status(self) -> bool:
        return self.is_terminated

    def get_players(self) -> list:
        return self.players

    def get_file_path(self) -> str:
        return self.file_path

    def terminate(self) -> None:
        self.is_terminated = True


@ray.remote
class Scraper:
    def __init__(self, game: int) -> None:
        """
        Web scraper base class.

        :game: fifa version
        """
        self.game = game
        self.players: List[object] = []

    def lookup(self, identifier: int) -> Union[object, None]:
        player = [p for p in self.players if p == identifier]
        return player[0] if player else None

    def update(self, storage: SharedStorage) -> None:
        while not ray.get(storage.get_terminate_status.remote()):  # type: ignore
            pid = ray.get(storage.get_pending_pid.remote())  # type: ignore
            player = Player(pid, self.game)

            try:
                attributes = player.download()
                if attributes:
                    _ = player.download_prices()
            except (SSLError, ProxyError):
                print("VPN blocked.")
                break
            except ValueError as e:
                print(pid, str(e))
                break
            except KeyboardInterrupt:
                break

            if attributes:
                storage.add_player.remote(player)  # type: ignore
