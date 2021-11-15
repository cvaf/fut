import os
from datetime import datetime

PARENT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
DATA_FOLDER = os.path.join(PARENT_FOLDER, "data")
LOGS_FOLDER = os.path.join(PARENT_FOLDER, "logs")
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

MAX_PIDS = {
    21: 31433,
    20: 50966,
    19: 21437,
}

COLUMNS = {
    "players": [
        "player_id",
        "game",
        "player_name",
        "overall",
        "quality",
        "resource_id",
        "player_key",
        "position",
        "num_games",
        "avg_goals",
        "avg_assists",
        "club",
        "nationality",
        "league",
        "skill_moves",
        "weak_foot",
        "intl_rep",
        "pref_foot",
        "height",
        "weight",
        "revision",
        "def_workrate",
        "att_workrate",
        "added_date",
        "origin",
        "age",
        "pace",
        "pace_acceleration",
        "pace_sprint_speed",
        "shooting",
        "shoot_positioning",
        "shoot_finishing",
        "shoot_shot_power",
        "shoot_long_shots",
        "shoot_volleys",
        "shoot_penalties",
        "passing",
        "pass_vision",
        "pass_crossing",
        "pass_free_kick",
        "pass_short",
        "pass_long",
        "pass_curve",
        "dribbling",
        "drib_agility",
        "drib_balance",
        "drib_reactions",
        "drib_ball_control",
        "drib_dribbling",
        "drib_composure",
        "defending",
        "def_interceptions",
        "def_heading",
        "def_marking",
        "def_stand_tackle",
        "def_slid_tackle",
        "physicality",
        "phys_jumping",
        "phys_stamina",
        "phys_strength",
        "phys_aggression",
    ],
    "prices": ["player_key", "date", "price"],
    "drop": ["player_name", "date", "relative_price", "player_key"],
    "temp": ["promo", "weekday", "days", "days_release", "availability", "price"],
    "attr": [
        "overall",
        "game",
        "club",
        "league",
        "nationality",
        "position",
        "height",
        "weight",
        "intl_rep",
        "pace",
        "pace_acceleration",
        "pace_sprint_speed",
        "dribbling",
        "drib_agility",
        "drib_balance",
        "drib_reactions",
        "drib_ball_control",
        "drib_dribbling",
        "drib_composure",
        "shooting",
        "shoot_positioning",
        "shoot_finishing",
        "shoot_shot_power",
        "shoot_long_shots",
        "shoot_volleys",
        "shoot_penalties",
        "passing",
        "pass_vision",
        "pass_crossing",
        "pass_free_kick",
        "pass_short",
        "pass_long",
        "pass_curve",
        "defending",
        "def_interceptions",
        "def_heading",
        "def_marking",
        "def_stand_tackle",
        "def_slid_tackle",
        "physicality",
        "phys_jumping",
        "phys_stamina",
        "phys_strength",
        "phys_aggression",
        "pref_foot",
        "att_workrate",
        "def_workrate",
        "weak_foot",
        "skill_moves",
        "source",
    ],
    "target": "price",
}

TOP = {
    "leagues": [
        "Premier League",
        "Serie A TIM",
        "LaLiga Santander",
        "Ligue 1 Conforama",
        "Bundesliga",
    ],
    "clubs": [
        "Manchester United",
        "Manchester City",
        "Chelsea",
        "Liverpool",
        "Arsenal",
        "Tottenham Hotspur",
        "Paris Saint-Germain",
        "Juventus",
        "Napoli",
        "FC Barcelona",
        "Real Madrid",
        "Atlético Madrid",
        "Borussia Dortmund",
        "FC Bayern München",
        "Piemonte Calcio",
        "Inter",
    ],
    "nations": [
        "Spain",
        "France",
        "Brazil",
        "Germany",
        "Argentina",
        "England",
        "Italy",
        "Portugal",
        "Holland",
        "Belgium",
    ],
}

PROMO_DATES = [
    [datetime(2020, 4, 24), datetime.now()],  # TOTSSF
    [datetime(2020, 3, 27), datetime(2020, 4, 11)],  # fut bday
    [datetime(2020, 2, 21), datetime(2020, 3, 5)],  # Shapeshift
    [datetime(2020, 1, 31), datetime(2020, 2, 14)],  # FFS
    [datetime(2020, 1, 17), datetime(2020, 1, 31)],  # headliners
    [datetime(2020, 1, 6), datetime(2020, 1, 13)],  # TOTY
    [datetime(2019, 12, 14), datetime(2019, 12, 24)],  # futmas
    [datetime(2019, 12, 6), datetime(2019, 12, 13)],  # TOTGS
    [datetime(2019, 11, 29), datetime(2019, 12, 1)],  # bl. friday
    [datetime(2019, 11, 8), datetime(2019, 11, 18)],  # RTTF
    [datetime(2019, 10, 18), datetime(2019, 10, 28)],  # halloween
    [datetime(2019, 5, 10), datetime(2019, 6, 21)],  # TOTS
    [datetime(2019, 4, 5), datetime(2019, 4, 15)],  # icon rel.
    [datetime(2019, 3, 22), datetime(2019, 3, 30)],  # fut bday
    [datetime(2019, 3, 8), datetime(2019, 3, 16)],  # carniball
    [datetime(2019, 2, 15), datetime(2019, 2, 24)],  # rating refr.
    [datetime(2019, 2, 1), datetime(2019, 2, 8)],  # headliners
    [datetime(2019, 1, 18), datetime(2019, 1, 25)],  # ffs
    [datetime(2019, 1, 7), datetime(2019, 1, 14)],  # TOTY
    [datetime(2018, 12, 14), datetime(2018, 12, 24)],  # futmas
    [datetime(2018, 12, 7), datetime(2018, 12, 14)],  # totgs
    [datetime(2018, 11, 23), datetime(2018, 11, 26)],  # bl. friday
    [datetime(2018, 11, 9), datetime(2018, 11, 16)],  # RTTF
    [datetime(2018, 10, 19), datetime(2018, 10, 26)],  # halloween
    [datetime(2018, 4, 27), datetime(2018, 5, 31)],  # TOTS
    [datetime(2018, 3, 16), datetime(2018, 3, 24)],  # fut bday
    [datetime(2018, 3, 9), datetime(2018, 3, 16)],  # Spring PTG
    [datetime(2018, 1, 17), datetime(2018, 1, 24)],  # TOTY
    [datetime(2017, 12, 8), datetime(2017, 12, 15)],  # TOTGS
    [datetime(2017, 11, 11), datetime(2017, 11, 21)],  # PTG
    [datetime(2017, 10, 20), datetime(2017, 10, 30)],  # halloween
]
