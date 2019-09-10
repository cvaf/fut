import pandas as pd
import numpy as np
from datetime import datetime
from db_functions import *

df_p = pd.read_csv('../data/player_database.csv', index_col='player_ID', parse_dates=['added_date'])

pgp_update = input('Fetch pgp?')              # y if true
price_update = input('Fetch prices?')         # y if true
latest_pid = int(input('Latest Player ID: ')) # ask for latest player id

df_p = df_fetch_newplayers(latest_pid, df_p)  # fetch all the new players
print('Finished fetching new players.')

# filter out some players
df_p = df_p[(df_p.quality == 'Gold - Rare') | (df_p.quality == 'Gold') | (df_p.quality == 'gold rare')]
df_p['revision'] = df_p.revision.fillna('Normal')
df_p = df_p[df_p.position != 'GK']

if pgp_update == 'y':
    print('Starting pgp update.')
    df_p = df_fetch_pgp_full(df_p)            # if asked, fetch pgp

df_p.to_csv('../data/player_database.csv')    # save the player dataframe
print('Player dataframe updated and saved.')

if price_update == 'y':
    df_prices = df_fetch_price_intervals(df_p)
    df_prices.to_csv('../data/prices_database.csv')