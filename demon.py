"""
Main script
"""
import click
import sys
import os

sys.path.append('modules')

from update import fetch_data
from preprocessing import run as process
from train import run as train_sophie
from evaluation import run as ev

@click.command()
@click.option('--update', is_flag=True, help='Fetch new players and prices')
@click.option('--train', is_flag=True, help='Train  the model')
@click.option('--validation', is_flag=True, help='Use a validation set')

def run(update, train, validation):

    if update:

        df_players, df_prices = fetch_data()
        process()

    if train:
        print('Training')
        train_sophie(validation=validation)

        if validation:
            print('Evaluating')
            evaluate()


if __name__ == '__main__':
    run()