from datetime import datetime
from numpy import dtype
date = datetime.now()

TOP_LEAGUES = ['Premier League', 'Serie A TIM', 'LaLiga Santander',
               'Ligue 1 Conforama', 'Bundesliga']


TOP_CLUBS = ['Manchester United', 'Manchester City', 'Chelsea', 'Liverpool',
             'Arsenal', 'Tottenham Hotspur', 'Paris Saint-Germain', 'Juventus',
             'Napoli', 'FC Barcelona', 'Real Madrid', 'Atlético Madrid',
             'Borussia Dortmund', 'FC Bayern München', 'Piemonte Calcio',
             'Inter']


TOP_NATIONS = ['Spain', 'France', 'Brazil', 'Germany', 'Argentina', 'England',
               'Italy', 'Portugal', 'Holland', 'Belgium']

PROMO_DATES = [[datetime(2020, 1, 17), datetime(2020, 1, 25)],    # headliners
               [datetime(2020, 1, 6), datetime(2020, 1, 13)],     # TOTY
               [datetime(2019, 12, 14), datetime(2019, 12, 24)],  # futmas
               [datetime(2019, 12, 6), datetime(2019, 12, 13)],   # TOTGS
               [datetime(2019, 11, 29), datetime(
                   2019, 12, 1)],   # black friday
               [datetime(2019, 11, 8), datetime(2019, 11, 18)],   # RTTF
               [datetime(2019, 10, 18), datetime(2019, 10, 28)],  # halloween
               [datetime(2019, 5, 10), datetime(2019, 6, 21)],    # TOTS
               [datetime(2019, 4, 5), datetime(
                   2019, 4, 15)],     # icon release
               [datetime(2019, 3, 22), datetime(2019, 3, 30)],    # fut bday
               [datetime(2019, 3, 8), datetime(2019, 3, 16)],     # carniball
               # rating refr.
               [datetime(2019, 2, 15), datetime(2019, 2, 24)],
               [datetime(2019, 2, 1), datetime(2019, 2, 8)],      # headliners
               [datetime(2019, 1, 18), datetime(2019, 1, 25)],    # ffs
               [datetime(2019, 1, 7), datetime(2019, 1, 14)],     # TOTY
               [datetime(2018, 12, 14), datetime(2018, 12, 24)],  # futmas
               [datetime(2018, 12, 7), datetime(2018, 12, 14)],   # totgs
               [datetime(2018, 11, 23), datetime(
                   2018, 11, 26)],  # black friday
               [datetime(2018, 11, 9), datetime(2018, 11, 16)],   # RTTF
               [datetime(2018, 10, 19), datetime(2018, 10, 26)]]  # halloween


# Number of past observations to look at
NUM_OBS = 7

# Number of forward steps to predict
NUM_STEPS = 3


# Column order
COLUMNS = ['player_name', 'revision', 'overall', 'club', 'league',
           'nationality', 'position', 'age', 'height', 'weight', 'intl_rep',
           'added_date', 'pace', 'pace_acceleration', 'pace_sprint_speed',
           'dribbling', 'drib_agility', 'drib_balance', 'drib_reactions',
           'drib_ball_control', 'drib_dribbling', 'drib_composure', 'shooting',
           'shoot_positioning', 'shoot_finishing', 'shoot_shot_power',
           'shoot_long_shots', 'shoot_volleys', 'shoot_penalties', 'passing',
           'pass_vision', 'pass_crossing', 'pass_free_kick', 'pass_short',
           'pass_long', 'pass_curve', 'defending', 'def_interceptions',
           'def_heading', 'def_marking', 'def_stand_tackle', 'def_slid_tackle',
           'physicality', 'phys_jumping', 'phys_stamina', 'phys_strength',
           'phys_aggression', 'pref_foot', 'att_workrate', 'def_workrate',
           'weak_foot', 'skill_moves', 'resource_id', 'num_games', 'avg_goals',
           'avg_assists', 'date', 'price']


COLUMN_DTYPES = [dtype('O'), dtype('O'), dtype('int64'), dtype('O'),
                 dtype('O'), dtype('O'), dtype('O'), dtype('int64'),
                 dtype('int64'), dtype('int64'), dtype('int64'),
                 dtype('<M8[ns]'), dtype('float64'), dtype('int64'),
                 dtype('int64'), dtype('float64'), dtype('int64'),
                 dtype('int64'), dtype('int64'), dtype('int64'),
                 dtype('int64'), dtype('int64'), dtype('float64'),
                 dtype('int64'), dtype('int64'), dtype('int64'),
                 dtype('int64'), dtype('int64'), dtype('int64'),
                 dtype('float64'), dtype('int64'), dtype('int64'),
                 dtype('int64'), dtype('int64'), dtype('int64'),
                 dtype('int64'), dtype('float64'), dtype('int64'),
                 dtype('int64'), dtype('int64'), dtype('int64'),
                 dtype('int64'), dtype('float64'), dtype('int64'),
                 dtype('int64'), dtype('int64'), dtype('int64'), dtype('O'),
                 dtype('O'), dtype('O'), dtype('int64'), dtype('int64'),
                 dtype('int64'), dtype('O'), dtype('O'), dtype('O'),
                 dtype('<M8[ns]'), dtype('int64')]


DROP_COLS = ['player_name', 'date', 'game', 'relative_price', 'custom_id']
TEMP_COLS = ['promo', 'weekday', 'days', 'days_release', 'price']
ATTR_COLS = ['overall', 'club', 'league', 'nationality', 'position', 'height',
             'weight', 'intl_rep', 'pace', 'pace_acceleration',
             'pace_sprint_speed', 'dribbling', 'drib_agility', 'drib_balance',
             'drib_reactions', 'drib_ball_control', 'drib_dribbling',
             'drib_composure', 'shooting', 'shoot_positioning',
             'shoot_finishing', 'shoot_shot_power', 'shoot_long_shots',
             'shoot_volleys', 'shoot_penalties', 'passing', 'pass_vision',
             'pass_crossing', 'pass_free_kick', 'pass_short', 'pass_long',
             'pass_curve', 'defending', 'def_interceptions', 'def_heading',
             'def_marking', 'def_stand_tackle', 'def_slid_tackle',
             'physicality', 'phys_jumping', 'phys_stamina', 'phys_strength',
             'phys_aggression', 'pref_foot', 'att_workrate', 'def_workrate',
             'weak_foot', 'skill_moves', 'source']
TARGET = 'price'

ckpt_date = 'weights' + str(int(date.month * 100) + int(date.day))
ckpt_name = ckpt_date + '.{epoch:02d}-{val_loss:.2f}.hdf5'
ckpt_path = 'models/checkpoints/' + ckpt_name
CHECKPOINT_DICT = {'folder': 'models/checkpoints',
                   'name': ckpt_name,
                   'path': ckpt_path}
