import ray
from time import sleep

from .scraper import Scraper, SharedStorage
from .utils import ProxyHandler


class Client:
    def __init__(self, game: int, num_workers: int) -> None:
        self.game = game
        self.num_workers = num_workers

        ray.init(num_gpus=1, ignore_reinit_error=True)
        self.storage_worker = None
        self.proxy_worker = None
        self.scraper_workers = None

    def run(self) -> None:

        self.storage_worker = SharedStorage.remote(game=self.game)  # type: ignore
        self.proxy_worker = ProxyHandler.remote()  # type: ignore

        self.scraper_workers = [
            Scraper.remote(self.game) for _ in range(self.num_workers - 2)  # type: ignore
        ]

        _ = [
            scraper.update.remote(self.storage_worker, self.proxy_worker)
            for scraper in self.scraper_workers  # type: ignore
        ]

        self._logging_loop()

    def _logging_loop(self) -> None:
        pending_pids = ray.get(self.storage_worker.get_pending.remote())  # type: ignore
        total_pids = len(pending_pids)
        try:
            while pending_pids:
                print(
                    f"Progress: {total_pids-len(pending_pids)}/{total_pids}",
                    end="\r",
                )
                sleep(0.5)
                pending_pids = ray.get(self.storage_worker.get_pending.remote())  # type: ignore
        except KeyboardInterrupt:
            pass
        self._terminate_workers()

    def _terminate_workers(self) -> None:
        """Softly terminate any running tasks"""
        self.storage_worker.terminate.remote()  # type: ignore
        self.storage_worker.save.remote()  # type: ignore

        self.storage_worker = None
        self.proxy_worker = None
        self.scraper_workers = None

    def shutdown(self) -> None:
        ray.shutdown()
