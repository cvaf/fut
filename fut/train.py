"""
Train/retrain sophie
"""

import os, sys
sys.path.append(os.getcwd())

import logging
from datetime import datetime, timedelta

# Custom modules
from fut.constants import NUM_OBS, NUM_STEPS
from fut.config import CHECKPOINT_DICT

# processing & model selection
import numpy as np
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

  array_files = [f'data/{x}' for x in os.listdir('data/') if '.npz' in x]
  latest_file = max(array_files, key=os.path.getctime)
  print('Latest file found: {}'.format(latest_file))
  latest_array = np.load(latest_file)
  logging.info(f'Array file: {latest_file}')

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

  logging.debug(f'Attribute input shape: {train_attr[0].shape}')
  logging.debug(f'Temporal input shape: {train_temp[0].shape}')

  input_attr = Input(shape=train_attr[0].shape)
  input_temp = Input(shape=train_temp[0].shape)

  # Temporal path
  X_temp1 = GRU(512, activation='relu', recurrent_activation='relu',
                dropout=0.1, recurrent_dropout=0.1,
                return_sequences=True)(input_temp)
  X_temp2 = GRU(256, activation='relu', recurrent_activation='relu',
                dropout=0.1, recurrent_dropout=0.1,
                return_sequences=True)(X_temp1)
  # X_temp3 = GRU(128, activation='relu', recurrent_activation='relu',
  #               dropout=0.1, recurrent_dropout=0.1,
  #               return_sequences=True)(X_temp2)
  X_temp3 = GRU(128, activation='relu', recurrent_activation='relu')(X_temp2)


  # Attribute path
  X_attr1 = Dense(512, activation='relu')(input_attr)
  X_attr2 = Dense(256, activation='relu')(X_attr1)
  X_attr3 = Dense(128, activation='relu')(X_attr2)


  # Merged path
  X = Concatenate(axis=1)([X_attr3, X_temp3])
  X = Dense(512, activation='relu')(X)
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
    logging.info(f'Checkpoint loaded: {latest_chkpt}')

  except:
    logging.info('No checkpoint loaded.')

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
  logging.info('Started training module.')

  logging.debug('Loading the arrays.')
  data = load_arrays()

  logging.debug('Defining model.')
  model = model_setup(data)

  logging.debug('Loading checkpoints.')
  model = load_checkpoints(model)

  logging.debug('Training model.')
  model, history = train(model, data, validation)

  if validation:
    val=1
  else:
    val=0

  model = load_checkpoints(model)
  model_num = str(datetime.now().strftime('%m%d'))
  model_name = f'models/{model_num}_{str(val)}.h5'
  model.save(model_name)
  logging.info(f'Model saved in: {model_name}')


if __name__ == '__main__':
  try:
    if sys.argv[1] == 'validation':
      run(validation=True)
  except:
    run()
