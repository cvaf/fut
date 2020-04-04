"""
Train/retrain sophie
"""

import numpy as np
import os
import sys
from datetime import datetime, timedelta

sys.path.append('modules')

# Custom modules
from constants import NUM_OBS, NUM_STEPS
from config import CHECKPOINT_DICT

# processing & model selection
import joblib
import tensorflow as tf
from tensorflow.keras.layers import Dense, Flatten, Input, Concatenate, GRU
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import Model

tf.random.set_seed(410)
np.random.seed(410)

date = datetime.now()

def load_arrays():
    """
    Load the processed arrays
    """

    array_files = [f'data/{x}' for x in os.listdir('data/') if '.npz' in x]
    latest_file = max(array_files, key=os.path.getctime)
    print('Latest file found: {}'.format(latest_file))
    latest_array = np.load(latest_file)

    data = {}
    for d in latest_array.files:
        data[d] = latest_array[d]

    return data

def model_setup(data):
    """
    Define the model
    """
    
    train_attr = data['train_attr']
    train_temp = data['train_temp']

    input_attr = Input(shape=train_attr[0].shape)
    input_temp = Input(shape=train_temp[0].shape)

    # Temporal path
    X_temp1 = GRU(256, activation='relu', recurrent_activation='relu',
                  dropout=0.1, recurrent_dropout=0.1,
                  return_sequences=True)(input_temp)
    X_temp2 = GRU(256, activation='relu', recurrent_activation='relu',
                  dropout=0.1, recurrent_dropout=0.1,
                  return_sequences=True)(X_temp1)
    X_temp3 = GRU(256, activation='relu', recurrent_activation='relu',
                  dropout=0.1, recurrent_dropout=0.1,
                  return_sequences=True)(X_temp2)
    X_temp4 = GRU(256, activation='relu', recurrent_activation='relu')(X_temp3)


    # Attribute path
    X_attr1 = Dense(256, activation='relu')(input_attr)
    X_attr2 = Dense(256, activation='relu')(X_attr1)
    X_attr3 = Dense(256, activation='relu')(X_attr2)
    X_attr4 = Dense(128, activation='relu')(X_attr3)


    # Merged path
    X = Concatenate(axis=1)([X_attr4, X_temp4])
    X = Dense(256, activation='relu')(X)
    X = Dense(256, activation='relu')(X)
    X = Dense(128, activation='relu')(X)
    output = Dense(NUM_STEPS, activation='relu')(X)

    model = Model([input_attr, input_temp], output)

    return model

def load_checkpoints(model):
    """
    Load the latest model checkpoints
    """

    checkpoint_folder = CHECKPOINT_DICT['folder']

    if not os.path.exists(checkpoint_folder):
        os.makedirs(checkpoint_folder)

    try:
        latest_chkpt_name = os.listdir(checkpoint_folder)[-1]
        latest_chkpt = os.path.join(checkpoint_folder, latest_chkpt_name)
        model.load_weights(latest_chkpt)
        print('Checkpoint loaded.')

    except:
        print('No checkpoints in the folder.')

    return model


def train(model, data, validation):
    """
    Initiate and train the model
    """

    optimizer = Adam()
    model.compile(optimizer=optimizer, loss='mse')

    # Callback list
    checkpoint_path = CHECKPOINT_DICT['path']
    callbacks_list = [EarlyStopping(monitor='val_loss', patience=4),
                      ModelCheckpoint(filepath=checkpoint_path,
                                      monitor='val_loss',
                                      save_best_only=True)]

    # Extract the data
    if validation:
        train_attr = data['train_attr']
        train_temp = data['train_temp']
        train_targ = data['train_targ']

    else:
        train_attr = data['total_attr']
        train_temp = data['total_temp']
        train_targ = data['total_targ']

    valid_attr = data['valid_attr']
    valid_temp = data['valid_temp']
    valid_targ = data['valid_targ']

    # Train
    history = model.fit([train_attr, train_temp], train_targ,
                        validation_data=([valid_attr, valid_temp], valid_targ),
                        callbacks=callbacks_list,
                        batch_size=32, epochs=30)

    return model, history


def run(validation=False):


    print('Loading the data...')
    # Load the data arrays
    data = load_arrays()
    print('Done.\n')


    # Define the model
    print('Defining the model...')
    model = model_setup(data)
    print('Done.\n')

    # Load the latest checkpoint if there are any
    print('Loading checkpoints...')
    model = load_checkpoints(model)
    print('Done.\n')


    # Train the model
    print('Training the model...')
    model, history = train(model, data, validation)
    print('Done.\n')

    if validation:
        val=1
    else:
        val=0

    print('Saving the model...')
    model = load_checkpoints(model)
    model_num = (int(date.month) * 100) + int(date.day) 
    model_name = 'models/{}_{}.h5'.format(str(model_num), str(val))
    model.save(model_name)
    print('Done.\n')


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'validation':
            run(validation=True)
    except:
        run()
