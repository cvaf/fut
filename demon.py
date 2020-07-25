#!/usr/bin/python3.7

import sys, os
sys.path.append(os.getcwd())

import logging
from datetime import datetime

sys.path.append('modules')

from fut.update import fetch_data
from fut.preprocessing import process
from fut.train import run as train_sophie
from fut.evaluation import run as evaluate
from fut.log import setup_logger

import click
@click.command()
@click.option('--update', is_flag=True, help='Fetch new players and prices')
@click.option('--train', is_flag=True, help='Train  the model')
@click.option('--validation', is_flag=True, help='Use a validation set')
@click.option('--log', default='info', help='Logging verbosity level.')

def run(update, train, validation, log):
  setup_logger()

  parameters = f"""
    U: {update}; T: {train}; V: {validation}; L: {log};
              """
  logging.info(parameters)


  if update:
    df_players, df_prices = fetch_data()
    logging.info('Processing new data.')
    process()

  if train:

    logging.info('Training.')
    train_sophie(validation=validation)

    if validation:
      logging.info('Evaluation.')
      evaluate()


if __name__ == '__main__':
  run()