from datetime import datetime

TOP_LEAGUES = ['Premier League', 'Serie A TIM', 'LaLiga Santander', 'Ligue 1 Conforama', 'Bundesliga']


TOP_CLUBS = ['Manchester United', 'Manchester City', 'Chelsea', 'Liverpool', 'Arsenal', 'Tottenham Hotspur',
            'Paris Saint-Germain', 'Juventus', 'Napoli', 'Inter', 'FC Barcelona', 'Real Madrid', 'Atlético Madrid',
            'Borussia Dortmund', 'FC Bayern München', 'Piemonte Calcio']


TOP_NATIONS = ['Spain', 'France', 'Brazil', 'Germany', 'Argentina', 'England',
               'Italy', 'Portugal', 'Holland', 'Belgium']

PROMO_DATES = [[datetime(2019, 10, 18), datetime(2019, 10, 28)],     # halloween
               [datetime(2019, 5, 10), datetime(2019, 6, 21)],       # TOTS
               [datetime(2019, 4, 5), datetime(2019, 4, 15)],        # icon release
               [datetime(2019, 3, 22), datetime(2019, 3, 30)],       # fut bday
               [datetime(2019, 3, 8), datetime(2019, 3, 16)],        # carniball
               [datetime(2019, 2, 15), datetime(2019, 2, 24)],       # rating refresh
               [datetime(2019, 2, 1), datetime(2019, 2, 8)],         # headliners
               [datetime(2019, 1, 18), datetime(2019, 1, 25)],       # ffs
               [datetime(2019, 1, 7), datetime(2019, 1, 14)],        # TOTY
               [datetime(2018, 12, 14), datetime(2018, 12, 24)],     # futmas
               [datetime(2018, 12, 7), datetime(2018, 12, 14)],      # totgs
               [datetime(2018, 11, 23), datetime(2018, 11, 26)],     # black friday
               [datetime(2018, 11, 9), datetime(2018, 11, 16)],      # rttf
               [datetime(2018, 10, 19), datetime(2018, 10, 26)]]     # halloween