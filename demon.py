#!/usr/bin/python 

import sys
import os

sys.path.append('modules')

from update import fetch_data
from preprocessing import run as process
from train import run as train_sophie
from evaluation import run as evaluate

import click
@click.command()
@click.option('--update', is_flag=True, help='Fetch new players and prices')
@click.option('--train', is_flag=True, help='Train  the model')
@click.option('--validation', is_flag=True, help='Use a validation set')
@click.option('--log', default='info', help='Logging verbosity level.')

def run(update, train, validation, log):

    # Set up logger

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