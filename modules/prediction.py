"""
Module containing functions for fetching a player's attributes and 
prices required to generate a prediction
"""

import pandas as pd
import numpy as np

# other
import os
import sys
from datetime import datetime
import joblib
import warnings
warnings.filterwarnings('ignore')

sys.path.append('modules')

# custom modules
from preprocessing import load_data, processing
from constants import NUM_OBS, NUM_STEPS

# modeling
from tensorflow.keras.models import load_model

temp_scaler = joblib.load('../models/temp_scaler.joblib')
price_scaler = joblib.load('../models/price_scaler.joblib')
attr_ct = joblib.load('../models/attr_ct.joblib')
latest_model = [x for x in os.listdir('../models') if '.h5' in x][-1]
model = load_model(f'../models/{latest_model}')


def temporal_transformation(df_temp, temp_scaler=temp_scaler, price_scaler=price_scaler):
	"""
	Scale the temporal data
	Arguments:
		- df_temp: dataframe indexed by resource_id, containing all temporal variables
					(date, promo, weekday, days, days_release, price)
	"""

	# Temporal variable scaling
	temp_num = ['weekday', 'days']
	df_temp[temp_num] = temp_scaler.transform(df_temp[temp_num].values)

	# Price scaling
	df_temp['price'] = price_scaler.transform(df_temp['price'].values.reshape(-1,1))

	temporal = df_temp.values
	return temporal


def attribute_transformation(df_attr, transformer=attr_ct):
	"""
	Scale the attribute data
	"""

	attributes = transformer.transform(df_attr)
	return attributes


def data_format(temporal, attributes, num_obs=NUM_OBS):
	"""
	Changing the data format for modeling
	"""
	attr = np.append(attributes, temporal[0][-1])
	temp = temporal[:, 1:]

	attr = np.asarray(attr)
	temp = np.asarray(temp)

	return attr, temp.astype(np.float64)


def generate_prediction(player_id):
	"""
	Complete prediction pipeline
	"""
	df = load_data(player_id)
	df = processing(df)

	# Column assignment
	drop_cols = ['player_name', 'resource_id', 'date', 'game', 'relative_price']
	temp_cols = ['promo', 'weekday', 'days', 'days_release', 'price']
	attr_cols = [c for c in df.columns if c not in (drop_cols + temp_cols)]
	target = 'price'

	# Temporal transformation
	df_temp = df.groupby(['resource_id', 'date'])[temp_cols].first().reset_index(1)
	temporal = temporal_transformation(df_temp)

	# Attributes transformation
	df_attr = df.groupby('resource_id')[attr_cols].first()
	attributes = attribute_transformation(df_attr)

	attr, temp = data_format(temporal, attributes)

	# Generate prediction
	preds = model.predict([[attr], [temp]])
	transformed_preds = price_scaler.inverse_transform(preds.reshape(1, -1))

	return transformed_preds


if __name__ == '__main__':

	player_id = int(sys.argv[1])
	preds = generate_prediction(player_id)

	print('Predictions:')
	print(preds)