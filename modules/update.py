"""
Module containing functions for updating the player
and prices dataframes
"""

import pandas as pd
import numpy as np

# other
from datetime import datetime
from time import time, strftime, localtime, sleep
import os
import sys

# scraping imports
from bs4 import BeautifulSoup
import json
import requests

# multiprocessing
from multiprocessing import Pool
from tqdm import tqdm




def vpn_reconnect():
    os.system('nordvpn d')
    sleep(3)
    os.system('nordvpn c')
    sleep(3)
    print('VPN reconnect.\n')




def fetch_player_soup(player_id):
    """
    Fetch the request and process it with bs4
    Arguments:
        - player_id: int, player's ID
    Returns:
        - soup: request
    """

    resp = requests.get('https://www.futbin.com/20/player/' + str(player_id))
    soup = BeautifulSoup(resp.text, features='lxml')

    if 'does not have permission' in soup.text:
        # _ = input('Access denied. Proceed?')
        print('Access denied.')
        vpn_reconnect()

        # vpn reconnect
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
    url = 'https://www.futbin.com/20/playerGraph?type=daily_graph&year=20&player=' + str(rid)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, features='lxml')
    if 'does not have permission' in soup.text:
        print('Access denied.')
        vpn_reconnect()
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




def fetch_player(player_id):
    """
    Fetch all relevant data on a particular player. 
    Arguments:
        - player_id: int, player's ID
    Returns:
        - data: dict, contains all requested attributes
    """

    soup = fetch_player_soup(player_id)

    data = [player_id]

    # exception in case there's no player at this ID
    try:
        player_name = soup.find('span', {'class': 'header_name'}).text
    except:
        for j in range(56):
            data.append(0)
        return data

    data.append(player_name)
    data.append(soup.find('h1', {'class': 'player_header header_top pb-0'}).text.strip()[:2])
    data.append(soup.find('div', {'id': 'Player-card'})['class'][-3] + ' ' + \
                      soup.find('div', {'id': 'Player-card'})['class'][-2])
    data.append(soup.find('div', {'id': 'page-info'})['data-player-resource'])
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

    # information
    info = soup.findAll('td', {'class': 'table-row-text'})

    # some are missing international reputation
    try:
        age = info[16].text.strip()
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


def fetch_df_players(num_processes=10):
    """
    Create or update the dataframe
    Arguments:
        - num_processes: how many processes to use in parallel
    Returns:
        - df: updated dataframe
    """

    # fetch the latest available pid
    latest_pid = fetch_latest_pid()

    # if no dataframe was passed, create one
    cols = ['player_id', 'player_name', 'overall', 'quality', 'resource_id', 'position', 
            'num_games', 'avg_goals', 'avg_assists','club', 'nationality', 'league', 'skill_moves',
            'weak_foot', 'intl_rep', 'pref_foot', 'height', 'weight', 'revision', 
            'def_workrate', 'att_workrate', 'added_date', 'origin', 'age', 'pace', 'pace_acceleration', 
            'pace_sprint_speed', 'shooting', 'shoot_positioning', 'shoot_finishing', 
            'shoot_shot_power', 'shoot_long_shots', 'shoot_volleys', 'shoot_penalties', 
            'passing', 'pass_vision', 'pass_crossing', 'pass_free_kick', 'pass_short', 
            'pass_long', 'pass_curve', 'dribbling', 'drib_agility', 'drib_balance', 
            'drib_reactions', 'drib_ball_control', 'drib_dribbling', 'drib_composure', 
            'defending', 'def_interceptions', 'def_heading', 'def_marking', 'def_stand_tackle',
            'def_slid_tackle', 'physicality', 'phys_jumping', 'phys_stamina', 'phys_strength', 
            'phys_aggression']

    if os.path.exists('../data/fifa20_players.pkl'):
        df = pd.read_pickle('../data/fifa20_players.pkl')
        current_pid = df.player_id.values[-1]
    else:
        df = pd.DataFrame(columns=cols)
        current_pid = 0


    # number of players to collect
    total_pids = latest_pid - current_pid
    pids = range(current_pid+1, latest_pid+1)

    with Pool(num_processes) as p:
        players_data = list(tqdm(p.imap(fetch_player, pids), total=total_pids))

    if df.shape[0] == 0:
        df = pd.DataFrame(data=players_data, columns=cols)
    else:
        new_df = pd.DataFrame(data=players_data, columns=cols)
        df = df.append(new_df)

    df = df[df.phys_aggression.notnull()].reset_index(drop=True)
    df.sort_values(by='player_id', ascending=True, inplace=True)

    return df


def fetch_df_prices(df_players, num_processes=10):
    """
    Function used to fetch the prices for all players in the players dataframe.
    
    Arguments:
        df_players: player dataframe
        num_processes: how many processes to use, default=10
    Returns:
        df_price: our new dataframe with the prices
    """

    rids = df_players.resource_id.values

    # number of players to collect
    total_rids = len(rids)
    
    with Pool(num_processes) as p:
        prices = list(tqdm(p.imap(fetch_price, rids), total=total_rids))

    prices = np.array(prices)
    prices = [x for x in prices if x != None]
    prices = np.concatenate(prices)

    df_prices = pd.DataFrame(prices, columns=['resource_id', 'date', 'price'])
    df = df_players.merge(df_prices, on='resource_id', how='left')
    return df


def fetch_data():
    """
    Create/update/load the players dataframe and create/update/load the prices dataframe.
    Arguments:
        - price_update: str, 'y' to update prices
        - save_file: boolean, True to save the dataframes
    """

    print('Fetching players...')
    df_players = fetch_df_players()
    df_players.to_pickle('../data/fifa20_players.pkl', protocol=4)
    print('DONE: df_players.\n')

    print('Fetching prices...')
    df_prices = fetch_df_prices(df_players)
    df_prices.to_pickle('../data/fifa20_prices.pkl', protocol=4)
    print('DONE: df_prices.\n')

    return df_players, df_prices


if __name__ == '__main__':
    df_players, df_prices =  fetch_data(price_update=price_update)