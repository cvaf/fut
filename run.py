import click
from fut import Client


@click.command()
@click.option(
    "--game", default=22, help="game to fetch data for. One of (19, 20, 21, 22)"
)
@click.option("--num_workers", default=4, help="Number of workers to use in parallel.")
def run(game: int, num_workers: int) -> None:

    if game not in {19, 20, 21, 22}:
        raise ValueError(f"Invalid game argument: {game}")
    elif num_workers < 4:
        raise ValueError("Number of workers must be greater than 3")

    client = Client(game, num_workers)
    client.run()
    client.shutdown()


if __name__ == "__main__":
    run()
