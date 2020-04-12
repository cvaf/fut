"""
Preprocessing script that prepares the raw data for modeling
"""
import os 
import sys

import pandas as pd
import numpy as np

sys.path.append('modules')

# other
from datetime import datetime, timedelta

# custom modules
from constants import PROMO_DATES, TOP_LEAGUES, TOP_CLUBS, TOP_NATIONS, \
    TEMP_COLS, ATTR_COLS, NUM_OBS, NUM_STEPS

import warnings
warnings.filterwarnings('ignore')

from sqlalchemy import create_engine

# model-related
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder


def load_data():
    """
    Load the player and prices dataframes and merge them together
    """
    engine = create_engine('sqlite:///data/fifa.db', echo=False)

    df_players = pd.read_sql_table('players', engine)
    df_prices = pd.read_sql_table('prices', engine)
    df = df_players.merge(df_prices, on=['player_key'], how='inner')

    return df


def promo_assignment(ds):
    """
    Promotional encoding function
    """
    date = pd.to_datetime(ds)
    promo = 0
    for p in PROMO_DATES:
        if (p[0] <= date) & (p[1] >= date):
            promo = 1
            break
    return promo



def processing(df):
    """
    Run the concatenated dataframe through the preprocessing pipeline
    """

    # Number of days between observation date and player added date
    df['days'] = (df.date - df.added_date).dt.days

    # Observation weekday
    df['weekday'] = df.date.dt.weekday

    # Encode the following variables: league, club and nationality
    df['league'] = np.where(df.league.isin(TOP_LEAGUES), 
                            df.league,
                            'other')
    df['club'] = np.where(df.club.isin(TOP_CLUBS), 
                          df.club,
                          'other')
    df['nationality'] = np.where(df.nationality.isin(TOP_NATIONS), 
                                 df.nationality, 
                                 'other')

    # Note if there was an active promotion at observation date
    df['promo'] = df['date'].apply(promo_assignment)

    # Source: whether the card was obtainable through packs, sbc or objectives
    # As we're only interested in cards obtainable through packs,
    # we can just remove the rest
    resources = df[df.price>0].resource_id.unique()
    df['source'] = np.where(df.resource_id.isin(resources), 'packs', 'other')
    df = df[df.source=='packs']

    # Days from release
    FIFA18_release = df[df.game=='FIFA18'].date.min()
    FIFA19_release = df[df.game=='FIFA19'].date.min()
    FIFA20_release = df[df.game=='FIFA20'].date.min()

    df['days_release'] = np.where(df.game=='FIFA19', 
                                 (df.date - FIFA19_release).dt.days,
                                 (df.date - FIFA20_release).dt.days)
    df['days_release'] = np.where(df.game=='FIFA18',
                                  (df.date - FIFA18_release).dt.days,
                                  df.days_release)
    df['days_release'] = df.days_release / 365    # scale it between 0 and 1


    # Relative price: how the price changed to the previous day
    df.sort_values(by=['game', 'resource_id', 'date'], 
                   ascending=True, inplace=True)
    df_ = df.shift(1)
    df['relative_price'] = np.where(df.resource_id == df.resource_id,
                                    df.price*100/df_.price,
                                    'first')
    df = df[df.relative_price!='first']

    # Add an availability variable
    df['availability'] = np.where(df.days<=7, 1, 0)
    df['availability'] = np.where(df.revision.isin(['Normal', 'CL']), 
                                  1, df.availability)

    # Remove some players
    revision_stopwords = ['SBC', 'POTM', 'Obj', 'Moments', 'League', 
                          'Special', 'FUTmas']
    good_revisions = [x for x in df.revision.unique() if not\
                      any(xs in x for xs in revision_stopwords)]
    df = df[df.revision.isin(good_revisions)].reset_index(drop=True)

    # Drop some columns
    drop_cols = ['revision', 'age', 'num_games', 
                 'added_date', 'avg_goals', 'avg_assists']
    df.drop(drop_cols, axis=1, inplace=True)

    # Remove players which aren't as relevant to our prediction problem
    df = df[(df.price!=0) & (df.overall>=83)].reset_index(drop=True)
    expensive_resources = df[df.price>2000000].resource_id.unique()
    df = df[~df.resource_id.isin(expensive_resources)]

    return df


def train_valid_split(df):
    """
    Create a validation set
    """
    cutoff_date = datetime.now() - timedelta(days=30)
    
    df_valid = df[df.date>cutoff_date]
    df_train = df[df.date<=cutoff_date]

    return df_train, df_valid



def temporal_transformation(df, train=True):

    df_temp = df.groupby(['player_key', 'date'])[TEMP_COLS].first().reset_index(1)
    temp_num = ['weekday', 'days']

    # Load transformers
    if train:
        temp_scaler = MinMaxScaler().fit(df_temp[temp_num].values)
        joblib.dump(temp_scaler, 'models/temp_scaler.joblib')
        price_scaler = MinMaxScaler().fit(df_temp.price.values.reshape(-1, 1))
        joblib.dump(price_scaler, 'models/price_scaler.joblib')
    else:
        temp_scaler = joblib.load('models/temp_scaler.joblib')
        price_scaler = joblib.load('models/price_scaler.joblib')

    # Temporal scaling
    df_temp[temp_num] = temp_scaler.transform(df_temp[temp_num].values)

    # Price scaling
    df_temp['price'] = price_scaler.transform(df_temp.price.values.reshape(-1, 1))

    return df_temp


def attribute_tranformation(df, train=True):

    df_attr = df.groupby('player_key')[ATTR_COLS].first()

    attr_cat = ['game', 'club', 'league', 'nationality', 'pref_foot', 
                'att_workrate', 'def_workrate', 'position', 'source', 
                'availability']
    attr_num = [v for v in df_attr.columns if v not in attr_cat]
    num_mask = df_attr.columns.isin(attr_num)

    if train:
        ct = make_column_transformer(
            (MinMaxScaler(), num_mask), 
            (OneHotEncoder(handle_unknown='ignore'), ~num_mask)
        )
        attr_ct = ct.fit(df_attr)
        joblib.dump(attr_ct, 'models/attr_ct.joblib')

    else:
        attr_ct = joblib.load('models/attr_ct.joblib')

    ids = df_attr.index.values
    data = attr_ct.transform(df_attr)
    data_dict = dict(zip(ids, data))

    return data_dict



def format(df, train=True):

    all_temp = temporal_transformation(df, train=train)
    all_attr = attribute_tranformation(df, train=train)

    pids = all_temp.index.unique().values

    pids_data = []
    targ_data = []
    temp_data = []
    attr_data = []

    for pid in pids:

        attributes = all_attr[pid]
        # attributes = df_attr[df_attr.index==pid].values[0]
        temporal_d = all_temp[all_temp.index==pid].values

        total_obs = temporal_d.shape[0]
        window_size = NUM_OBS + NUM_STEPS

        if window_size > total_obs:
            continue

        for i in range(total_obs - window_size):

            attr = np.append(attributes, temporal_d[i+NUM_OBS-1][-1])
            temp = temporal_d[i:i+NUM_OBS][:, 1:]
            targ = temporal_d[i+NUM_OBS:i+NUM_OBS+NUM_STEPS][:, -1]
            targ_data.append(targ)
            temp_data.append(temp)
            attr_data.append(attr)
            pids_data.append(pid)

    pids_array = np.asarray(pids_data)
    targ_array = np.asarray(targ_data).astype(np.float64)
    temp_array = np.asarray(temp_data).astype(np.float64)
    attr_array = np.asarray(attr_data)


    assert pids_array.shape[0] == temp_array.shape[0] \
           == targ_array.shape[0] == attr_array.shape[0]

    return pids_array, targ_array, temp_array, attr_array


def run():
    """
    Load the data, process it and return the correct data format
    """

    print('Loading the data...')
    df = load_data()
    print('Done.\n')

    print('Processing...')
    df = processing(df)
    print('Done.\n')

    df_train, df_valid = train_valid_split(df)

    print('Formatting...')
    total_pids, total_targ, total_temp, total_attr = format(df)
    train_pids, train_targ, train_temp, train_attr = format(df_train, train=False)
    valid_pids, valid_targ, valid_temp, valid_attr = format(df_valid, train=False)
    print('Done.\n')
    
    datestamp = datetime.now().strftime('%Y%m%d')
    file_name = f'data/{datestamp}.npz'
    np.savez(file_name, 
             total_pids=total_pids, total_targ=total_targ, 
             total_temp=total_temp, total_attr=total_attr,
             train_pids=train_pids, train_targ=train_targ, 
             train_temp=train_temp, train_attr=train_attr, 
             valid_pids=valid_pids, valid_targ=valid_targ,
             valid_temp=valid_temp, valid_attr=valid_attr)

    print('DONE: preprocessing.\n')


if __name__ == '__main__':
    run()