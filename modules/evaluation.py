"""
Model evaluation script
"""
import pandas as pd 
import numpy as np 
import os
import sys

# Custom modules
from train import load_arrays

# Model related imports
from tensorflow.keras.models import load_model
import joblib


def load_latest():
    """
    Load the latest model in our models directory
    """

    model_folder = 'models/'
    all_models = [os.path.join(model_folder, x) \
                  for x in os.listdir(model_folder) if '_1.h5' in x]
    model_file = max(all_models, key=os.path.getctime)
    model = load_model(model_file)
    model_name = model_file.split('/')[1][:-3]
    
    return model, model_name



def generate_predictions(model):
    """
    Use the model to generate predictions for the data
    """
    data = load_arrays()
    price_scaler = joblib.load('models/price_scaler.joblib')

    attr = data['valid_attr']
    temp = data['valid_temp']
    targ = data['valid_targ']
    pids = data['valid_pids']

    # Dictionary to store the predictions and targets
    evaluation_data = {}

    # Store the player IDs
    evaluation_data['pids'] = pids

    # Store the transformed predictions
    preds = model.predict([attr, temp])
    evaluation_data['preds'] = price_scaler.inverse_transform(preds)

    # Store the transformed target
    evaluation_data['target'] = price_scaler.inverse_transform(targ)

    # Store each player's latest actual price
    prices = temp[:, -1, -1].reshape(-1, 1)
    evaluation_data['prices'] = price_scaler.inverse_transform(prices)

    return evaluation_data



def evaluate_predictions(data):
    """
    Analyze the model's predictions to determine its performance
    by grouping the predictions into bins.
    """

    # Change prediction format to percentage change in price
    data['preds_perc'] = data['preds'] / data['prices']
    data['target_perc'] = data['target'] / data['prices']

    df = pd.DataFrame(data=data['pids'], columns=['pids'])

    # Create the boundaries for the bins
    bin_bounds = [(0, 0.6, 4),      # Bin4: >40% decrease
                  (0.6, 0.8, 3),    # Bin3: 20-40% decrease
                  (0.8, 0.95, 2),   # Bin2: 5-20% decrease
                  (0.95, 1.05, 1),  # Bin1: <=5% change
                  (1.05, 1.2, 2),   # Bin2: 5-20% increase
                  (1.2, 1.4, 3),    # Bin3: 20-40% increase
                  (1.4, 10, 4)]     # Bin4: >40% increase

    for i in range(3):

        # Create an evaluation col to log whether the prediction 
        # for that step was accurate
        eva_col = 'eva{}'.format(i)
        df[eva_col] = 0


        # Find the prediction and target for that step
        preds = np.asarray(data['preds_perc'][:, i])
        target = np.asarray(data['target_perc'][:, i])

        for bounds in bin_bounds:
            b = bounds[2]
            lower_b = bounds[0]
            upper_b = bounds[1]

            preds_condition = (lower_b < preds) & (preds < upper_b)
            target_condition = (lower_b < target) & (target < upper_b)


            df[eva_col] = np.where((preds_condition) & (target_condition),
                                   b,
                                   df[eva_col])

        # Create an accuracy column to log the model accuracy
        acc_col = 'acc{}'.format(i)
        df[acc_col] = np.where(df[eva_col] == 0, 0, 1)

    df = df.groupby(['pids']).mean().reset_index()


    # Remove game from player id
    # df['pids'] = df.pids.apply(lambda x: x[:-2])

    # Create a weighted accuracy and evaluation rating
    df['eva'] = ((df.eva0 * 3) + (df.eva1 * 2) + (df.eva2)) / 6
    df['acc'] = ((df.acc0 * 3) + (df.acc1 * 2) + (df.acc2)) / 6

    df = df[['pids', 'eva', 'acc']].round(2)

    return df


def run():

    print('Loading latest model...')
    # Load the latest model
    model, model_name = load_latest()
    print('Done: Loaded {}\n'.format(model_name))

    print('Generating predictions...')
    # Produce predictions for our validation set
    data = generate_predictions(model)
    print('Done.\n')

    # Evaluate the predictions generated above.
    print('Evaluating predictions...')
    df = evaluate_predictions(data)
    print('Done.\n')

    df.to_pickle('data/evaluation_{}.pkl'.format(model_name), protocol=4)





if __name__ == '__main__':
    run()