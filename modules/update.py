"""
Module containing functions for updating the player
and prices dataframes
"""

import os
import sys

sys.path.append('modules')

import pandas as pd
import numpy as np
from datetime import datetime
from time import time, strftime, localtime, sleep

# scraping imports
from bs4 import BeautifulSoup
import json
import requests
from multiprocessing import Pool
from tqdm import tqdm

from constants import BASE_URL, COLUMNS_PLAYERS, COLUMN_TYPES


def fetch_player_soup(player_id):
    """
    Fetch the request and process it with bs4
    Arguments:
        - player_id: int, player's ID
    Returns:
        - soup: request
    """

    resp = requests.get(BASE_URL + '/20/player/' + str(player_id))
    soup = BeautifulSoup(resp.text, features='lxml')

    if 'does not have permission' in soup.text:
        # _ = input('Access denied. Proceed?')
        print('Access denied.')
        os.system('say "Please reconnect."')
        proc = input('Proceed?')
        if proc == 'y':
            soup = fetch_soup(player_id)

    return soup


def fetch_price_soup(rid):
    """
    Fetch the price request and process it
    Arguments:
        - rid: int, player's resource id
    Returns:
        - soup: requested soup
    """
    url = BASE_URL + '20/playerGraph?type=daily_graph&year=20&player=' + str(rid)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, features='lxml')

    if 'does not have permission' in soup.text:
        print('Access denied.')
        os.system('say "Please reconnect."')
        proc = input('Proceed?')
        if proc == 'y':
            soup = fetch_price_soup(rid)

    return soup


def fetch_price(rid):
    """
    Fetch the prices for a specific player
    Arguments:
        - rid: int, player's resource id
    Returns:
        - prices: list of dictionaries
    """

    prices = []
    soup = fetch_price_soup(rid)
    try:
        price_data = json.loads(soup.text)['ps']
        for i in price_data:
            row = [rid]
            row.append(strftime('%Y-%m-%d', localtime(i[0]/1000)))
            row.append(i[1])
            prices.append(row)
        return prices

    except:
        print('No prices available for rid: {}'.format(rid))


def fetch_player(player_id, game='20'):
    """
    Fetch all relevant data on a particular player. 
    Arguments:
        - player_id: int, player's ID
    Returns:
        - data: dict, contains all requested attributes
    """

    soup = fetch_player_soup(player_id)

    data = [player_id, f'FIFA{game}']

    info = soup.findAll('td', {'class': 'table-row-text'})
    # exception in case there's no player at this ID
    try:
        player_name = info[0].text
    except:
        for j in range(56):
            data.append(0)
        return data

    data.append(player_name)


    try: 
        rating = soup.find('div', {'class': 'pcdisplay-rate'}).text
    except:
        rating = soup.find('div', {'class': 'pcdisplay-rat'}).text
    data.append(rating)
    
    quality = soup.find('div', {'id': 'Player-card'})['class'][-3] + ' ' + \
        soup.find('div', {'id': 'Player-card'})['class'][-2]
    data.append(quality)

    resource_id = soup.find('div', {'id': 'page-info'})['data-player-resource']
    data.append(resource_id)

    player_key = f'{resource_id}_{game}'
    data.append(player_key)

    position = soup.find('div', {'id': 'page-info'})['data-position']
    data.append(position)

    if position == 'GK':
        for j in range(52):
            data.append(0)
        return data

    # PGP
    player_stats = soup.findAll('div', {'class': 'ps4-pgp-data'})
    data.append(player_stats[-1].text.split()[-1])
    data.append(player_stats[-2].text.split()[-1])
    data.append(player_stats[-3].text.split()[-1])

    # some are missing international reputation
    try:
        age = info[17].text.strip()
        for i in range(1, 15):
            if i == 8:
                stat = info[i].text.strip()[:3]
            else:
                stat = info[i].text.strip()

            data.append(stat)
        data.append(age)
    except:
        for i in range(1, 6):
            stat = info[i].text.strip()
            data.append(stat)
        stat = 0
        data.append(stat)
        for i in range(6, 14):
            if i == 7:
                stat = info[i].text.strip()[:3]
            else:
                stat = info[i].text.strip()
            data.append(stat)
        data.append(info[15].text.strip())


    # attributes
    stats = json.loads(soup.find('div', {'id': 'player_stats_json'}).text.strip())

    ## PACE
    for i in range(3):
        stat = stats[0]['pace'][i]['value']
        data.append(stat)

    ## SHOOTING
    for i in range(7):
        stat = stats[0]['shooting'][i]['value']
        data.append(stat)

    ## PASSING
    for i in range(7):
        stat = stats[0]['passing'][i]['value']
        data.append(stat)

    ## DRIBBLING
    for i in range(7):
        stat = stats[0]['dribbling'][i]['value']
        data.append(stat)

    ## DEFENDING
    for i in range(6):
        stat = stats[0]['defending'][i]['value']
        data.append(stat)

    ## PHYSICAL
    for i in range(5):
        stat = stats[0]['physical'][i]['value']
        data.append(stat)

    return data


def fetch_latest_pid():
    """
    Find the latest player id 
    """
    resp = requests.get('https://www.futbin.com/latest')
    soup = BeautifulSoup(resp.text, 'lxml')
    pid = soup.find_all('table')[0].find('a').attrs['href'].split('/')[3]
    return int(pid)


def fetch_df_players(engine, num_processes=10):
    """
    Create or update the dataframe
    Arguments:
        - num_processes: how many processes to use in parallel
    Returns:
        - df: updated dataframe
    """

    # fetch the latest available pid
    latest_pid = fetch_latest_pid()

    # Find the latest player_id

    ## TODO Confirm this works once we have sqlite setup
    try:
        query = """
            SELECT MAX(player_id)
            FROM players
            WHERE game='FIFA20'
                """
        current_pid = engine.execute(query)[0]

    except:
        current_pid = 0

    # number of players to collect
    total_pids = latest_pid - current_pid
    pids = range(current_pid+1, latest_pid+1)

    with Pool(num_processes) as p:
        players_data = list(tqdm(p.imap(fetch_player, pids), total=total_pids))

    df = pd.DataFrame(data=players_data, columns=COLUMNS_PLAYERS)

    df = df[df.phys_aggression.notnull()].reset_index(drop=True)
    df.sort_values(by='player_id', ascending=True, inplace=True)

    return df


def fetch_df_prices(engine, num_processes=10):
    """
    Function used to fetch the prices for all players in the players dataframe.
    
    Arguments:
        engine: sqlite connection object
        num_processes: int
            How many processes to use. Default=10
    Returns:
        df_prices: pandas dataframe
            ['player_key', 'resource_id', 'price']
    """

    query = """
        SELECT
            player_key, 
            resource_id
        FROM players
        WHERE game = 'FIFA20'
            """

    df_keys = pd.read_sql_query(query, engine)

    rids = df_keys.resource_id.values

    # number of players to collect
    total_rids = len(rids)
    
    with Pool(num_processes) as p:
        prices = list(tqdm(p.imap(fetch_price, rids), total=total_rids))

    prices = np.array(prices)
    prices = [x for x in prices if x != None]
    prices = np.concatenate(prices)

    df_prices = pd.DataFrame(prices, columns=['resource_id', 'date', 'price'])
    df_prices = df_prices.merge(df_keys, on='resource_id', how='inner')
    df_prices = df_prices[['player_key', 'date', 'price']]

    # Load the prices from the older games.
    query_old = """
        SELECT
            player_key,
            date,
            price
        FROM prices
        WHERE game != 'FIFA20'
                """
    df_old_prices = pd.read_sql_query(query_old, engine)
    df_prices = df_old_prices.append(df_prices)
    df_prices.reset_index(drop=True, inplace=True)

    return df_prices


def fetch_data(engine):
    """
    Create/update/load the players dataframe and create/update/load the prices dataframe.
    """

    print('Fetching players...')
    df_players = fetch_df_players(engine)
    try:
        df_players.to_sql('players', engine, index=False, dtype=COLUMN_TYPES, 
            if_exists='append')
    except:
        print('Saving locally.')
        df_players.to_pickle('data/fifa20_newplayers.pkl', protocol=4)
    print('DONE: df_players.\n')

    print('Fetching prices...')
    df_prices = fetch_df_prices(engine)
    try: 
        df_prices.to_sql('prices', engine, index=False, dtype=COLUMN_TYPES,
            if_exists='replace')
    except:
        print('Saving locally')
        df_prices.to_pickle('data/fifa20_newprices.pkl', protocol=4)
    print('DONE: df_prices.\n')

    return df_players, df_prices


if __name__ == '__main__':
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///data/fifa.db', echo=False)
    df_players, df_prices =  fetch_data(engine)