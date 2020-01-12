"""
Module containing functions for fetching a player's attributes and 
prices required to generate a prediction
"""

import pandas as pd
import numpy as np

# other
import os
import sys
sys.path.append('../database')

# scraping
from bs4 import BeautifulSoup
from xlml import html, etree
from urllib.request import urlopen
import json
import requests
from update import fetch_player, fetch_price


def fetch_player_latest(player_id):
    """
    Fetch a player's attributes and prices required to generate 
    the prediction.
    """

    # fetch the player's attributes
    player_data = fetch_player(player_id)
    resource_id = player_data[3]
    cols = ['player_id', 'player_name', 'overall', 'quality', 'resource_id', 'position', 
            'num_games', 'avg_goals', 'avg_assists','club', 'nationality', 'league', 'skill_moves',
            'weak_foot', 'intl_rep', 'pref_foot', 'height', 'weight', 'revision', 
            'def_workrate', 'att_workrate', 'added_date', 'origin', 'age', 'pace', 'pace_acceleration', 
            'pace_sprint_speed', 'shooting', 'shoot_positioning', 'shoot_finishing', 
            'shoot_shot_power', 'shoot_long_shots', 'shoot_volleys', 'shoot_penalties', 
            'passing', 'pass_vision', 'pass_crossing', 'pass_free_kick', 'pass_short', 
            'pass_long', 'pass_curve', 'dribbling', 'drib_agility', 'drib_balance', 
            'drib_reactions', 'drib_ball_control', 'drib_dribbling', 'drib_composure', 
            'defending', 'def_interceptions', 'def_heading', 'def_marking', 'def_stand_tackle',
            'def_slid_tackle', 'physicality', 'phys_jumping', 'phys_stamina', 'phys_strength', 
            'phys_aggression']

    df_player = pd.DataFrame(data=player_data, columns=cols)

    # fetch the player's prices
    prices = fetch_price(resource_id)
    latest_prices = prices[-7:]
    assert len(latest_prices) == 7
    df_prices = pd.DataFrame(latest_prices, 
    						 columns=['resource_id', 'date', 'price'])

    # merge the attributes and the prices
    df = df_player.merge(df_prices, on='resource_id', how='left')

    return df 


# def preprocess(df):
# 	"""
# 	Run the player dataframe through the processing script
# 	"""

	