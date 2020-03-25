BASE_URL = 'https://www.futbin.com' 

TOP_LEAGUES = [
    'Premier League', 'Serie A TIM', 'LaLiga Santander',
    'Ligue 1 Conforama', 'Bundesliga'
    ]

TOP_CLUBS = [
    'Manchester United', 'Manchester City', 'Chelsea', 'Liverpool',
    'Arsenal', 'Tottenham Hotspur', 'Paris Saint-Germain', 'Juventus',
    'Napoli', 'FC Barcelona', 'Real Madrid', 'Atlético Madrid',
    'Borussia Dortmund', 'FC Bayern München', 'Piemonte Calcio','Inter'
    ]

TOP_NATIONS = [
    'Spain', 'France', 'Brazil', 'Germany', 'Argentina', 'England',
    'Italy', 'Portugal', 'Holland', 'Belgium'
    ]

from datetime import datetime
PROMO_DATES = [
    [datetime(2020, 2, 21), datetime(2020, 3, 5)],     # Shapeshift
    [datetime(2020, 1, 31), datetime(2020, 2, 14)],    # FFS
    [datetime(2020, 1, 17), datetime(2020, 1, 31)],    # headliners
    [datetime(2020, 1, 6), datetime(2020, 1, 13)],     # TOTY
    [datetime(2019, 12, 14), datetime(2019, 12, 24)],  # futmas
    [datetime(2019, 12, 6), datetime(2019, 12, 13)],   # TOTGS
    [datetime(2019, 11, 29), datetime(2019, 12, 1)],   # bl. friday
    [datetime(2019, 11, 8), datetime(2019, 11, 18)],   # RTTF
    [datetime(2019, 10, 18), datetime(2019, 10, 28)],  # halloween
    [datetime(2019, 5, 10), datetime(2019, 6, 21)],    # TOTS
    [datetime(2019, 4, 5), datetime(2019, 4, 15)],     # icon rel.
    [datetime(2019, 3, 22), datetime(2019, 3, 30)],    # fut bday
    [datetime(2019, 3, 8), datetime(2019, 3, 16)],     # carniball
    [datetime(2019, 2, 15), datetime(2019, 2, 24)],    # rating refr.
    [datetime(2019, 2, 1), datetime(2019, 2, 8)],      # headliners
    [datetime(2019, 1, 18), datetime(2019, 1, 25)],    # ffs
    [datetime(2019, 1, 7), datetime(2019, 1, 14)],     # TOTY
    [datetime(2018, 12, 14), datetime(2018, 12, 24)],  # futmas
    [datetime(2018, 12, 7), datetime(2018, 12, 14)],   # totgs
    [datetime(2018, 11, 23), datetime(2018, 11, 26)],  # bl. friday
    [datetime(2018, 11, 9), datetime(2018, 11, 16)],   # RTTF
    [datetime(2018, 10, 19), datetime(2018, 10, 26)],  # halloween
    [datetime(2018, 4, 27), datetime(2018, 5, 31)],    # TOTS
    [datetime(2018, 3, 16), datetime(2018, 3, 24)],    # fut bday
    [datetime(2018, 3, 9), datetime(2018, 3, 16)],     # Spring PTG
    [datetime(2018, 1, 17), datetime(2018, 1, 24)],    # TOTY
    [datetime(2017, 12, 8), datetime(2017, 12, 15)],   #TOTGS
    [datetime(2017, 11, 11), datetime(2017, 11, 21)],  # PTG
    [datetime(2017, 10, 20), datetime(2017, 10, 30)]   # halloween
    ]

# Number of past observations to look at
NUM_OBS = 7

# Number of forward steps to predict
NUM_STEPS = 3

# Column types
from sqlalchemy.types import String, Float, Integer, DateTime
COLUMN_TYPES = {
    'player_id': Integer(),
    'game': String(),
    'player_name': String(),
    'overall': Integer(),
    'quality': String(),
    'resource_id': Integer(),
    'player_key': String(),
    'position': String(),
    'num_games': Integer(),
    'avg_goals': Float(),
    'avg_assists': Float(),
    'club': String(),
    'league': String(),
    'nationality': String(),
    'skill_moves': Integer(),
    'weak_foot': Integer(),
    'pref_foot': String(),
    'age': Integer(),
    'height': Float(),
    'weight': Float(),
    'revision': String(),
    'intl_rep': Integer(),
    'def_workrate': String(),
    'att_workrate': String(),
    'added_date': DateTime(),
    'origin': String(),
    'pace': Integer(),
    'pace_acceleration': Integer(),
    'pace_sprint_speed': Integer(),
    'shooting': Integer(),
    'shoot_positioning': Integer(),
    'shoot_finishing': Integer(),
    'shoot_shot_power': Integer(),
    'shoot_long_shots': Integer(),
    'shoot_volleys': Integer(),
    'shoot_penalties': Integer(),
    'passing': Integer(),
    'pass_vision': Integer(),
    'pass_crossing': Integer(),
    'pass_free_kick': Integer(),
    'pass_short': Integer(),
    'pass_long': Integer(),
    'pass_curve': Integer(),
    'dribbling': Integer(),
    'drib_agility': Integer(),
    'drib_balance': Integer(),
    'drib_reactions': Integer(),
    'drib_ball_control': Integer(),
    'drib_dribbling': Integer(),
    'drib_composure': Integer(),
    'defending': Integer(),
    'def_interceptions': Integer(),
    'def_heading': Integer(),
    'def_marking': Integer(),
    'def_stand_tackle': Integer(),
    'def_slid_tackle': Integer(),
    'physicality': Integer(),
    'phys_jumping': Integer(),
    'phys_stamina': Integer(),
    'phys_strength': Integer(),
    'phys_aggression': Integer(),
    'date': DateTime(),
    'price': Float()
}


COLUMNS_PLAYERS = [
    'player_id', 'game', 'player_name', 'overall', 'quality', 'resource_id', 
    'player_key', 'position', 'num_games', 'avg_goals', 'avg_assists','club', 
    'nationality', 'league', 'skill_moves', 'weak_foot', 'intl_rep', 
    'pref_foot', 'height', 'weight', 'revision', 'def_workrate', 'att_workrate',
    'added_date', 'origin', 'age', 'pace', 'pace_acceleration', 
    'pace_sprint_speed', 'shooting', 'shoot_positioning', 'shoot_finishing',
    'shoot_shot_power', 'shoot_long_shots', 'shoot_volleys', 'shoot_penalties',
    'passing', 'pass_vision', 'pass_crossing', 'pass_free_kick', 'pass_short', 
    'pass_long', 'pass_curve', 'dribbling', 'drib_agility', 'drib_balance',
    'drib_reactions', 'drib_ball_control', 'drib_dribbling', 'drib_composure',
    'defending', 'def_interceptions', 'def_heading', 'def_marking', 
    'def_stand_tackle', 'def_slid_tackle', 'physicality', 'phys_jumping', 
    'phys_stamina', 'phys_strength', 'phys_aggression'
    ]


# COLUMNS = ['player_name', 'revision', 'overall', 'club', 'league',
#            'nationality', 'position', 'age', 'height', 'weight', 'intl_rep',
#            'added_date', 'pace', 'pace_acceleration', 'pace_sprint_speed',
#            'dribbling', 'drib_agility', 'drib_balance', 'drib_reactions',
#            'drib_ball_control', 'drib_dribbling', 'drib_composure', 'shooting',
#            'shoot_positioning', 'shoot_finishing', 'shoot_shot_power',
#            'shoot_long_shots', 'shoot_volleys', 'shoot_penalties', 'passing',
#            'pass_vision', 'pass_crossing', 'pass_free_kick', 'pass_short',
#            'pass_long', 'pass_curve', 'defending', 'def_interceptions',
#            'def_heading', 'def_marking', 'def_stand_tackle', 'def_slid_tackle',
#            'physicality', 'phys_jumping', 'phys_stamina', 'phys_strength',
#            'phys_aggression', 'pref_foot', 'att_workrate', 'def_workrate',
#            'weak_foot', 'skill_moves', 'resource_id', 'num_games', 'avg_goals',
#            'avg_assists', 'date', 'price']

# from numpy import dtype
# COLUMN_DTYPES = [dtype('O'), dtype('O'), dtype('int64'), dtype('O'),
#                  dtype('O'), dtype('O'), dtype('O'), dtype('int64'),
#                  dtype('int64'), dtype('int64'), dtype('int64'),
#                  dtype('<M8[ns]'), dtype('float64'), dtype('int64'),
#                  dtype('int64'), dtype('float64'), dtype('int64'),
#                  dtype('int64'), dtype('int64'), dtype('int64'),
#                  dtype('int64'), dtype('int64'), dtype('float64'),
#                  dtype('int64'), dtype('int64'), dtype('int64'),
#                  dtype('int64'), dtype('int64'), dtype('int64'),
#                  dtype('float64'), dtype('int64'), dtype('int64'),
#                  dtype('int64'), dtype('int64'), dtype('int64'),
#                  dtype('int64'), dtype('float64'), dtype('int64'),
#                  dtype('int64'), dtype('int64'), dtype('int64'),
#                  dtype('int64'), dtype('float64'), dtype('int64'),
#                  dtype('int64'), dtype('int64'), dtype('int64'), dtype('O'),
#                  dtype('O'), dtype('O'), dtype('int64'), dtype('int64'),
#                  dtype('int64'), dtype('O'), dtype('O'), dtype('O'),
#                  dtype('<M8[ns]'), dtype('int64')]

DROP_COLS = [
    'player_name', 'date', 'game', 'relative_price', 'player_key'
    ]
TEMP_COLS = [
    'promo', 'weekday', 'days', 'days_release', 'availability', 'price'
    ]
ATTR_COLS = [
    'overall', 'club', 'league', 'nationality', 'position', 'height', 'weight', 
    'intl_rep', 'pace', 'pace_acceleration', 'pace_sprint_speed', 'dribbling', 
    'drib_agility', 'drib_balance', 'drib_reactions', 'drib_ball_control', 
    'drib_dribbling', 'drib_composure', 'shooting', 'shoot_positioning',
    'shoot_finishing', 'shoot_shot_power', 'shoot_long_shots', 'shoot_volleys', 
    'shoot_penalties', 'passing', 'pass_vision', 'pass_crossing', 
    'pass_free_kick', 'pass_short', 'pass_long', 'pass_curve', 'defending', 
    'def_interceptions', 'def_heading', 'def_marking', 'def_stand_tackle', 
    'def_slid_tackle', 'physicality', 'phys_jumping', 'phys_stamina',
    'phys_strength', 'phys_aggression', 'pref_foot', 'att_workrate',
    'def_workrate', 'weak_foot', 'skill_moves', 'source'
    ]
TARGET = 'price'