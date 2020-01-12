"""
Script that prepares the raw dataset for modeling
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from time import time
import warnings
warnings.filterwarnings('ignore')
from pickle import dump

from sophie_config import TOP_LEAGUES, TOP_CLUBS, TOP_NATIONS, PROMO_DATES

# Load the fifa 19 dataframe
df_19 = pd.read_csv('../data/fifa19_prices.csv', index_col='Unnamed: 0', parse_dates=['added_date', 'date'])
df_19.drop('quality', axis=1, inplace=True)
df_19 = df_19[df_19.club!='Icons'].reset_index(drop=True)

# Load the fifa 20 pickle
df_20 = pd.read_pickle('../data/fifa20_prices.pkl')
df_20 = df_20[df_20.club!='Icons'].reset_index(drop=True)
df_20 = df_20[df_19.columns]

# Fix the age column in df20
df_20['age'] = df_20.age.apply(lambda x: x.split(' ')[0]).astype(int)
df_20 = df_20.dropna(subset=['price']).reset_index(drop=True)

# Align the dtypes between the two dataframes
for i in range(df_19.shape[1]):
    col = df_20.columns[i]
    dtype = df_19.dtypes[i]
    df_20[col] = df_20[col].astype(dtype)

# Create a game column and join the two dataframes together
df_19['game'] = 'FIFA 19'
df_20['game'] = 'FIFA 20'
df = df_19.append(df_20)

num_players = df.groupby('game').resource_id.nunique().sum()


## FEATURE ENGINEERING ##

# Days: number of days between observation date and added date
df['days'] = (df.date - df.added_date).dt.days

# Weekday: observation weekday
df['weekday'] = df.date.dt.weekday

# Club/League/Nation: Group everything into popular/non-popular

# Top leagues
df['league'] = np.where(df.league.isin(TOP_LEAGUES), 'top', 'other')

# Top clubs
df['club'] = np.where(df.club.isin(TOP_CLUBS), 'top', 'other')

# Top nations
df['nationality'] = np.where(df.nationality.isin(TOP_NATIONS), 'top', 'other')

# Promo
def promo_assignment(ds):
    date = pd.to_datetime(ds)
    promo = 0
    for p in PROMO_DATES:
        if (p[0] <= date) & (p[1] >= date):
            promo = 1
            break
    return promo

df['promo'] = df['date'].apply(promo_assignment)

# Source: whether the card was obtainable through packs, sbc or objectives
df.revision.fillna('MLS POTM', inplace=True)
df['source'] = 'packs'
# base cards
base = ['Normal', 'Winter Refresh']
df['source'] = np.where(df.revision.isin(base), 'packs', df.source)
# sbc cards
sbc = ['SBC', 'POTM']
df['source'] = np.where(df.revision.apply(lambda x: any(i.lower() in x.lower() for i in sbc)), 'sbc', df.source)
# loan cards
df['source'] = np.where(df.revision.str.contains('Loan'), 'loan', df.source) 
df = df[df.source != 'loan'] # remove loans
# objective cards
df['source'] = np.where(df.revision.str.contains('Ob'), 'objective', df.source)
# overwrite source for cards that were both objectives and in packs (TOTS Rodri)
resources = df[df.price>0].resource_id.unique()
df['source'] = np.where(df.resource_id.isin(resources), 'packs', df.source)

# Only keep cards that were in packs
df = df[df.source=='packs']

# Days from release
release_f19 = df[df.game=='FIFA 19'].date.min()
release_f20 = df[df.game=='FIFA 20'].date.min()
df['days_release'] = np.where(df.game=='FIFA 19', (df.date - release_f19).dt.days, (df.date - release_f20).dt.days)
df['days_release'] = df.days_release / 365

# Relative price: how the price changed to the day before
df.sort_values(by=['game', 'resource_id', 'date'], ascending=True, inplace=True)
df_ = df.shift(1)
df['relative_price'] = np.where(df.resource_id == df_.resource_id, df.price*100/df_.price, 'first')
df = df[df.relative_price!='first']

# Drop some columns
drop_cols = ['revision', 'age', 'num_games', 'added_date', 'avg_goals', 'avg_assists']
df.drop(drop_cols, axis=1, inplace=True)

# Remove players which aren't as relevant to our problem
df = df[(df.price!=0) & (df.overall>=84)].reset_index(drop=True)
df.head(2)

# Eliminate "expensive" players -- outliers basically
expensive_resources = df[df.price>1000000].resource_id.unique()
df=df[~df.resource_id.isin(expensive_resources)]


# Save the final dataframe on disk
df.to_pickle('../data/sofa_dataset.pkl', protocol=4)

print('Done.')