"""
Main script
"""
import click
import sys
sys.path.append('modules')

from update import fetch_data
from preprocessing import run as process
from train import run as train_sophie
from evaluation import run as evaluate

def option_to_boolean(option):
    if option == 'y':
        return True
    else:
        return False

@click.command()
@click.option('--update', default='n', help='Use y to fetch new players and prices')
@click.option('--train', default='n', help='Use y to train  the model')
@click.option('--validation', default='n', help='Use y to use a validation set')

def run(update, train, validation):

    validation = option_to_boolean(validation)
    update = option_to_boolean(update)
    train = option_to_boolean(train)

    if update:

        # Update the dataframes and save them locally
        df_players, df_prices = fetch_data()

        # Process the updated data and save it as an array
        process()

    if train:
        print('Training')
        # Retrain the model
        train_sophie(validation=validation)

        # If there's a validation set, produce an evaluation dataframe 
        if validation:
            print('Evaluating')
            evaluate()


if __name__ == '__main__':
    run()