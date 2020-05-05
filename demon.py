#!/usr/bin/python3.7

import sys
import os
import logging
from datetime import datetime

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
  log_numeric = getattr(logging, log.upper())
  if not isinstance(log_numeric, int):
    error_msg = f'Invalid log level: {log}'
    raise click.BadParameter(error_msg)

  timestamp = str(datetime.now().strftime('%Y%m%d_%H%M%S'))
  logging.basicConfig(filename=f'logs/{timestamp}.log',
    filemode='w', level=log_numeric, datefmt='%H:%M:%S', 
    format='%(asctime)s - %(levelname)s: %(message)s')

  parameters = f"""
    U: {update}; T: {train}; V: {validation}; L: {log};
              """
  logging.info(parameters)


  if update:

    logging.info('Fetching data.')
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