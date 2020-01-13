"""
Preprocessing script that prepares the raw data for modeling
"""

import pandas as pd
import numpy as np

# other
import sys
sys.path.append('../database')
from datetime import datetime, timedelta


from config import TOP_LEAGUES, TOP_CLUBS, TOP_NATIONS, PROMO_DATES, COLUMNS, COLUMN_DTYPES
from update import fetch_player, fetch_price


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



def pipeline(df):
    """
    Run the concatenated dataframe through the preprocessing pipeline
    """

    # Number of days between observation date and player added date
    df['days'] = (df.date - df.added_date).dt.days

    # Observation weekday
    df['weekday'] = df.date.dt.weekday

    # Encode the following variables: league, club and nationality
    df['league'] = np.where(df.league.isin(TOP_LEAGUES), 'top', 'other')
    df['club'] = np.where(df.club.isin(TOP_CLUBS), 'top', 'other')
    df['nationality'] = np.where(df.nationality.isin(TOP_NATIONS), 'top', 'other')

    # Note if there was an active promotion at observation date
    df['promo'] = df['date'].apply(promo_assignment)

    # Source: whether the card was obtainable through packs, sbc or objectives
    # As we're only interested in cards obtainable through packs we can just remove the rest
    resources = df[df.price>0].resource_id.unique()
    df['source'] = np.where(df.resource_id.isin(resources), 'packs', 'other')
    df = df[df.source=='packs']

    # Days from release
    if df.game.nunique() > 1:
        FIFA19_release = df[df.game=='FIFA 19'].date.min()
        FIFA20_release = df[df.game=='FIFA 20'].date.min()

        df['days_release'] = np.where(df.game=='FIFA 19', 
                                     (df.date - FIFA19_release).dt.days,
                                     (df.date - FIFA20_release).dt.days)
    else:
        FIFA20_release = datetime(2019, 9, 20)
        df['days_release'] = (df.date - FIFA20_release).dt.days

    df['days_release'] = df.days_release / 365    # scale it between 0 and 1


    # Relative price: how the price changed to the previous day
    df.sort_values(by=['game', 'resource_id', 'date'], ascending=True, inplace=True)
    df_ = df.shift(1)
    df['relative_price'] = np.where(df.resource_id == df.resource_id,
                                    df.price*100/df_.price,
                                    'first')
    df = df[df.relative_price!='first']

    # Drop some columns
    drop_cols = ['revision', 'age', 'num_games', 'added_date', 'avg_goals', 'avg_assists']
    df.drop(drop_cols, axis=1, inplace=True)

    return df



def fetch_data(player_id):
    """
    Fetch a player's attributes and the prices required to generate a prediction
    """
    player_data = fetch_player(player_id)

    # Parse the player's age
    age_idx = 23
    age = player_data[age_idx]
    stripped_age = age.split(' ')
    if stripped_age[-1] == 'old':
        age = int(stripped_age[0])
    else:
        current_date = datetime.today()
        birthday = datetime.strptime(age, '%d-%m-%Y')
        age = int((current_date - birthday).days / 365.25)
    player_data[age_idx] = age

    # Store the player's data in a dataframe
    cols = ['player_id', 'player_name', 'overall', 'quality', 'resource_id', 'position', 
            'num_games', 'avg_goals', 'avg_assists','club', 'nationality', 'league', 'skill_moves',
            'weak_foot', 'intl_rep', 'pref_foot', 'height', 'weight', 'revision', 
            'def_workrate', 'att_workrate', 'added_date', 'origin', 'age', 'pace', 
            'pace_acceleration', 'pace_sprint_speed', 'shooting', 'shoot_positioning', 
            'shoot_finishing', 'shoot_shot_power', 'shoot_long_shots', 'shoot_volleys', 
            'shoot_penalties', 'passing', 'pass_vision', 'pass_crossing', 'pass_free_kick', 
            'pass_short', 'pass_long', 'pass_curve', 'dribbling', 'drib_agility', 'drib_balance', 
            'drib_reactions', 'drib_ball_control', 'drib_dribbling', 'drib_composure', 
            'defending', 'def_interceptions', 'def_heading', 'def_marking', 'def_stand_tackle',
            'def_slid_tackle', 'physicality', 'phys_jumping', 'phys_stamina', 'phys_strength', 
            'phys_aggression']

    df_player = pd.DataFrame(data=[player_data], columns=cols)

    # Fetch the player's prices
    resource_id = player_data[4]
    prices = fetch_price(resource_id)
    latest_prices = prices[-7:]
    assert len(latest_prices) == 7
    df_prices = pd.DataFrame(latest_prices, columns=['resource_id', 'date', 'price'])

    # Merge the two dataframes
    df = df_player.merge(df_prices, on='resource_id', how='left')
    df = df[COLUMNS]
    for i in range(len(COLUMNS)):
        col = COLUMNS[i]
        dtype = COLUMN_DTYPES[i]
        df[col] = df[col].astype(dtype)
    df['game'] = 'FIFA 20'

    return df

# def prediction_pipeline(player_id):
#     """
#     Complete prediction pipeline
#     """

#     # Fetch the data and run it through the original pipeline
#     df = fetch_data(player_id)
#     df = pipeline(df)

#     # Postprocessing adjustments
#     drop_cols = ['player_name', 'resource_id', 'date', 'game', 'relative_price']
#     temp_cols = ['promo', 'weekday', 'days', 'days_release', 'price']



if __name__ == '__main__':

    # Load FIFA 19 dataframe
    df_19 = pd.read_csv('../data/fifa19_prices.csv', index_col='Unnamed: 0',
                        parse_dates=['added_date', 'date'])
    df_19.drop('quality', axis=1, inplace=True)
    df_19 = df_19[df_19!='Icons'].reset_index(drop=True)


    # Load FIFA 20 dataframe
    df_20 = pd.read_pickle('../data/fifa20_prices.pkl')
    df_20 = df_20[df_20.club!='Icons']
    df_20 = df_20[df_19.columns]
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

    df = pipeline(df)

    # Remove players which aren't as relevant to our prediction problem
    df = df[(df.price!=0) & (df.overall>=84)].reset_index(drop=True)
    expensive_resources = df[df.price>1000000].resource_id.unique()
    df = df[~df.resource_id.isin(expensive_resources)]

    # Save the preprocessed dataset to disk
    df.to_pickle('../data/sofa_dataset.pkl', protocol=4)
    print('Done processing.')