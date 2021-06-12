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

        self.storage_worker = SharedStorage.remote(game=self.game)
        self.proxy_worker = ProxyHandler.remote()

        self.scraper_workers = [
            Scraper.remote(self.game) for _ in range(self.num_workers - 2)
        ]

        _ = [
            scraper.update.remote(self.storage_worker, self.proxy_worker)
            for scraper in self.scraper_workers
        ]

        self._logging_loop()

    def _logging_loop(self) -> None:
        all_pids = pending_pids = ray.get(self.storage_worker.get_pending.remote())
        try:
            while pending_pids:
                print(
                    f"Progress: {len(all_pids)-len(pending_pids)}/{len(all_pids)}",
                    end="\r",
                )
                sleep(0.5)
                pending_pids = ray.get(self.storage_worker.get_pending.remote())
        except KeyboardInterrupt:
            pass
        self._terminate_workers()

    def _terminate_workers(self) -> None:
        """Softly terminate any running tasks"""
        self.storage_worker.terminate.remote()
        self.storage_worker.save.remote()

        self.storage_worker = None
        self.proxy_worker = None
        self.scraper_workers = None

    def shutdown(self) -> None:
        ray.shutdown()
