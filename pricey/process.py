# data processing for RNN model

import pandas as pd
import numpy as np

# other
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

np.random.seed(410)


df = pd.read_csv('../data/prices_database.csv', index_col='Unnamed: 0', parse_dates=['added_date', 'date'])

########################################################################
## FOLLOWING IS THE FEATURE ENGINEERING AS SEEN IN THE DEMON NOTEBOOK ##
########################################################################
def feat_engineer(df):
	"""
	Perform feature engineering and prepare dataset for transformation
	"""

	df = df[df.club != 'Icons']  # drop icons

	# days
	df['days'] = (df['date'] - df['added_date']).dt.days

	# fix offset of some observations
	offset_resources = df[df.days == -1].resource_id.unique()
	df['date'] = np.where(df.resource_id.isin(offset_resources), 
	                      df.date +pd.DateOffset(days=1), 
	                      df.date)
	df['days'] = (df.date - df.added_date).dt.days 
	df = df[df.days >= 0]
	df['days'] = df.days / 365
	df['days'] = np.log(df.days.values) - np.log(1-df.days.values)

	# weekday
	df['weekday'] = df.date.dt.weekday

	# general position
	for_pos = ['ST', 'CF', 'CAM', 'LW', 'LF', 'LM', 'RW', 'RF', 'RM']
	mid_pos = ['CM', 'CDM']
	def_pos = ['LB', 'LWB', 'CB', 'RB', 'RWB']
	df['gen_pos'] = np.where(df.position.isin(for_pos), 'forward', np.nan)
	df['gen_pos'] = np.where(df.position.isin(mid_pos), 'midfielder', df.gen_pos)
	df['gen_pos'] = np.where(df.position.isin(def_pos), 'defender', df.gen_pos)

	# group leagues
	t_leagues = ['Premier League', 'Serie A TIM', 'LaLiga Santander', 
				 'Ligue 1 Conforama', 'Bundesliga']
	df['league'] = np.where(df.league.isin(t_leagues), df.league, 'other')

	# group clubs
	t_clubs = ['Manchester United', 'Manchester City', 'Chelsea', 'Liverpool',
				'Arsenal', 'Tottenham Hotspur', 'Paris Saint-Germain', 'Juventus', 
				'Napoli', 'Inter', 'FC Barcelona', 'Real Madrid', 
				'Atlético Madrid','Borussia Dortmund', 'FC Bayern München']
	df['club'] = np.where(df.club.isin(t_clubs), df.club, 'other')

	# group nationalities
	t_nations = ['Spain', 'France', 'Brazil', 'Germany', 'Argentina', 'England',
				 'Italy', 'Portugal', 'Holland', 'Belgium']
	df['nationality'] = np.where(df.nationality.isin(t_nations), df.nationality, 'other')


	# promo
	promos = [[datetime(2019, 5, 10), datetime(2019, 6, 21)],       # TOTS
	          [datetime(2019, 4, 5), datetime(2019, 4, 15)],        # icon release
	          [datetime(2019, 3, 22), datetime(2019, 3, 30)],       # fut bday
	          [datetime(2019, 3, 8), datetime(2019, 3, 16)],        # carniball
	          [datetime(2019, 2, 15), datetime(2019, 2, 24)],       # RRefresh
	          [datetime(2019, 2, 1), datetime(2019, 2, 8)],         # headliners
	          [datetime(2019, 1, 18), datetime(2019, 1, 25)],       # FFS
	          [datetime(2019, 1, 7), datetime(2019, 1, 14)],        # TOTY
	          [datetime(2018, 12, 14), datetime(2018, 12, 24)],     # futmas
	          [datetime(2018, 12, 7), datetime(2018, 12, 14)],      # TOTGS
	          [datetime(2018, 11, 23), datetime(2018, 11, 26)],     # black friday
	          [datetime(2018, 11, 9), datetime(2018, 11, 16)],      # RTTF
	          [datetime(2018, 10, 19), datetime(2018, 10, 26)]]     # halloween

	def promo_assignment(ds):
	    date = pd.to_datetime(ds)
	    promo = 0
	    for p in promos:
	        if (p[0] <= date) & (p[1] >= date):
	            promo = 1
	            break
	    return promo

	df['promo'] = df['date'].apply(promo_assignment)

	# card source
	df.revision.fillna('MLS POTM', inplace=True)
	df['source'] = 'packs'
	base = ['Normal', 'Winter Refresh']
	df['source'] = np.where(df.revision.isin(base), 'packs', df.source)
	sbc = ['SBC', 'POTM']
	is_sbc = lambda x: any(i.lower() in x.lower() for i in sbc)
	df['source'] = np.where(is_sbc, 'sbc', df.source)
	df['source'] = np.where(df.revision.str.contains('Loan'), 'loan', df.source) 
	df = df[df.source != 'loan'] # remove loans
	df['source'] = np.where(df.revision.str.contains('Ob'), 'objective', df.source)
	resources = df[df.price>0].resource_id.unique()
	df['source'] = np.where(df.resource_id.isin(resources), 'packs', df.source)

	# availability
	df['available'] = np.nan
	is_special = ((df.source == 'packs') | (df.source == 'sbc') | (df.source == 'objective'))
	is_available = (df.date <= (df.added_date + pd.DateOffset(7)))
	df['available'] = np.where(is_special & is_available, 1, df.available)
	# create a cross product to find the availability of base cards from special pack cards
	base = df[df.source == 'base'][['player_name', 'age', 'height', 'weight', 'intl_rep', 
									'date', 'added_date', 'available', 'resource_id']]
	pack = df[df.source == 'packs'][['player_name', 'age', 'height', 'weight', 'intl_rep', 
									 'date', 'added_date', 'available']]
	overlap = base.merge(pack, on=['player_name', 'age', 'height', 'weight', 'intl_rep', 'date'], 
						 how='inner', suffixes=('', '_special'))
	overlap['available'] = np.where(overlap.available_special == 1, 0, 1)
	overlap = overlap.groupby(['player_name', 'age', 'height', 'weight', 'intl_rep', 'date', 'added_date', 'resource_id']).available.min().reset_index()
	df_ = df.merge(overlap, on=['date', 'resource_id' ,'added_date', 'player_name'], how='left', suffixes=('', '_overlap'))
	df['available'] = np.where(df.source == 'base', df_.available_overlap, df.available)
	df['available'] = np.where((df.source == 'base') & (df.available.isnull()), 1, df.available)
	df.available.fillna(0, inplace=True)

	# days since release
	df['days_release'] = (df.date - df.date.min()).dt.days / 365
	df['days_release'] = np.log(df.days_release) - np.log(1-df.days_release)

	# pgp
	df['avg_goals'] = pd.to_numeric(df.avg_goals.replace('-', 0))
	df['avg_assists'] = pd.to_numeric(df.avg_assists.replace('-', 0))

	# drop unwanted columns
	drop_cols = ['quality', 'revision', 'age', 'pace', 'pace_acceleration', 'pace_sprint_speed', 'drib_agility',
				 'drib_balance', 'drib_reactions', 'drib_ball_control', 'drib_dribbling', 'shoot_positioning', 
				 'shoot_finishing', 'shoot_shot_power', 'shoot_long_shots', 'shoot_volleys', 'shoot_penalties', 
				 'pass_vision', 'pass_crossing', 'pass_free_kick', 'pass_short', 'pass_long', 'pass_curve', 
				 'def_interceptions', 'def_heading', 'def_marking', 'def_stand_tackle', 'def_slid_tackle', 'phys_jumping',
				 'phys_strength', 'phys_aggression', 'pref_foot', 'num_games', 'price', 'added_date', 'position']
	df.drop(drop_cols, axis=1, inplace=True)

	return df







