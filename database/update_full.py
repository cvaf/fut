import pandas as pd
import numpy as np
from update import fetch_df_players, fetch_df_prices
import sys

try:
	price_update = str(sys.argv[1])
	print(price_update)
except:
	price_update = input('Fetch prices?')

df_players = fetch_df_players()
df_players.to_pickle('../data/fifa20_players.pkl')
print('DONE: df_players.\n')

if price_update=='y':
	print('Fetching prices...')
	df_prices = fetch_df_prices(df_players)
	df_prices.to_pickle('../data/fifa20_prices.pkl')
	print('DONE: df_prices.\n')