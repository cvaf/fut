"""
Train/retrain sophie
"""
import numpy as np

import os
import sys
from datetime import datetime, timedelta

# processing & model selection
import joblib
import tensorflow as tf
from tensorflow.keras.layers import Dense, Flatten, Input, Concatenate, GRU
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import Model

tf.random.set_seed(410)
np.random.seed(410)

def load_arrays():
    """
    Load the processed arrays
    """

    array_files = [x for x in os.listdir('../data/') if '.npz' in x]
    latest_file = np.sort(arrays)[-1]
    latest_array = np.load(latest)

    data = {}
    for d in latest_array.files:
        data[d] = latest_array[d]

    return data

def model():
    """
    Define and initiate the model
    """
    

if __name__ == '__main__':
    run()
