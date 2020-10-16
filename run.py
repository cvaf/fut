#!/usr/bin/python3.8

import os
import logging
import click

from fut.helpers import Scraper
from fut.utils import setup_logger


@click.command()
@click.option(
    "--update", is_flag=True, help="Download new player data and refresh prices")
@click.option(
    "--game", default=21, help="Game to fetch data for. One of (19, 20, 21)")
@click.option("--log", default="info", help="Logging verbosity level.")
def run(update, game, log):

    if game not in {19, 20, 21}:
        raise ValueError(f'Invalid game argument: {game}')

    setup_logger(log)

    parameters = f"""U: {update}; G: {game}; L: {log};"""
    logging.info(parameters)

    if update:

        if f'scraper{game}.pkl' in os.listdir('data'):
            s = Scraper.load(game)
        else:
            s = Scraper(game)

        s.update_players()
        s.save()

        s.update_prices()
        s.save()

if __name__ == "__main__":
    run()
