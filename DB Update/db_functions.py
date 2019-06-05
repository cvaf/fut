import pandas as pd
import numpy as np
from datetime import datetime
from bs4 import BeautifulSoup
from lxml import html, etree
from urllib.request import urlopen
import requests
from time import time, strftime, localtime
import json

def player_fetch_resourceid(player_id):
    """
    Function to find the resource id for a given player_id
    
    Arguments: 
        player_id: Futbin unique player ID
        
    Returns: 
        resource_id: The equivalent resource_id (string)
    """
    resp = requests.get('https://www.futbin.com/19/player/' + str(player_id))
    soup = BeautifulSoup(resp.text, 'html')
    resource = soup.find('div', {'id': 'page-info'})['data-player-resource']
    return resource



def df_fetch_resourceid(dataframe):
    """
    Function to fetch the resource_id for every player in our dataframe that doesn't have one
    
    Arguments:
        dataframe: Our dataframe
        
    Returns:
        dataframe: An updated dataframe with the resource_ids
    """
    # mask our dataframe for players with no resource_id
    df_ = dataframe[dataframe.resource_id.isnull()]
    start_time = time()
    i = 0
    for player_id in df_.index:
        df_.loc[player_id, 'resource_id'] = player_fetch_resourceid(player_id)
        i += 1
        if i % 500 == 0:
            print('Completed {} players. Time elapsed: {} seconds.'.format(i, 
                                                                           int(time() - start_time)))
    dataframe[dataframe.resource_id.isnull()] = df_
    return dataframe


def player_fetch_pgp(player_id):
    """
    Function to find the pgp data for a given player_id
    
    Arguments: 
        player_id: Futbin unique player ID
        
    Returns: 
        num_games, num_goals, num_assists: The equivalent statistics
    """
    resp = requests.get('https://www.futbin.com/19/player/' + str(player_id))
    soup = BeautifulSoup(resp.text, 'html')
    player_stats = soup.findAll('div', {'class': 'ps4-pgp-data'})
    num_games = player_stats[-1].text.split()[-1]
    num_goals = player_stats[-2].text.split()[-1]
    num_assists = player_stats[-3].text.split()[-1]
    return num_games, num_goals, num_assists

def df_fetch_pgp(dataframe):
    """
    Function to fetch the pgp data for every player in our dataframe that doesn't have it
    
    Arguments:
        dataframe: Our dataframe
        
    Returns:
        dataframe: An updated dataframe with the resource_ids
    """
    # mask our dataframe for players with no resource_id
    df_ = dataframe[dataframe.num_games.isnull()]
    tot_players = df_.shape[0]
    start_time = time()
    i = 0
    for player_id in df_.index:
        num_games, num_goals, num_assists = player_fetch_pgp(player_id)
        df_.loc[player_id, 'num_games'] = num_games
        df_.loc[player_id, 'avg_goals'] = num_goals
        df_.loc[player_id, 'avg_assists'] = num_assists
        i += 1
        if i % 200 == 0:
            print('Completed {} players. Time elapsed: {} seconds.'.format(i, 
                                                                           int(time() - start_time)))
            seconds_left = int((int(time() - start_time) / i) * (tot_players - i))
            print('Approximate time left: {} seconds.'.format(seconds_left))
    dataframe[dataframe.num_games.isnull()] = df_
    return dataframe


def df_fetch_pgp_full(dataframe):
    """
    Identif function to df_fetch_pgp but for all players
    
    Arguments:
        dataframe: our player dataframe
    Returns:
        dataframe: the updated player dataframe
    """
    tot_players = dataframe.shape[0]
    start_time = time(); i = 0        # for tracking purposes
    for player_id in dataframe.index:
        num_games, num_goals, num_assists = player_fetch_pgp(player_id)
        dataframe.loc[player_id, 'num_games'] = num_games
        dataframe.loc[player_id, 'avg_goals'] = num_goals
        dataframe.loc[player_id, 'avg_assists'] = num_assists
        i+=1                          # increment the tracking
        if i % 200 == 0:
            print('Completed {} players. Time elapsed: {} seconds.'.format(i, int(time() - start_time)))
            seconds_left = int((int(time() - start_time) / i) * (tot_players - i))
            print('Approximate time left: {} seconds.'.format(seconds_left))
    return dataframe


def player_fetch_all(player_id):
    """
    Function used to fetch all the relevant data on a particular player from futbin.
    
    Arguments: 
        player_id: the respective player_id
        
    Returns:
        data: A dictionary containing the relevant statistics.
    """
    resp = requests.get('https://www.futbin.com/19/player/' + str(player_id))
    soup = BeautifulSoup(resp.text, 'html')
    
    # initialize our stats dictionary
    data = {}
    data['player_name'] = soup.find('span', {'class': 'header_name'}).text
    data['overall'] = soup.find('h1', {'class': 'player_header header_top pb-0'}).text.strip()[:2]
    data['quality'] = soup.find('div', {'id': 'Player-card'})['class'][-3] + ' ' + soup.find('div', {'id': 'Player-card'})['class'][-2]
    data['resource_id'] = soup.find('div', {'id': 'page-info'})['data-player-resource']
    data['position'] = soup.find('div', {'id': 'page-info'})['data-position']
    player_stats = soup.findAll('div', {'class': 'ps4-pgp-data'})
    data['num_games'] = player_stats[-1].text.split()[-1]
    data['avg_goals'] = player_stats[-2].text.split()[-1]
    data['avg_assists'] = player_stats[-3].text.split()[-1]
    
    # collect player's information
    info = soup.findAll('td', {'class': 'table-row-text'})
    data['club'] = info[1].text.strip()
    data['nationality'] = info[2].text.strip()
    data['league'] = info[3].text.strip()
    data['skill_moves'] = info[4].text.strip()
    data['weak_foot'] = info[5].text.strip()
    data['intl_rep'] = info[6].text.strip()
    data['pref_foot'] = info[7].text.strip()
    data['height'] = info[8].text.strip()[:3]
    data['weight'] = info[9].text.strip()
    data['revision'] = info[10].text.strip()
    data['def_workrate'] = info[11].text.strip()
    data['att_workrate'] = info[12].text.strip()
    data['added_date'] = info[13].text.strip()
    data['age'] = info[16].text.strip()[:2]
    
    # collect player's stats
    stats = json.loads(soup.find('div', {'id': 'player_stats_json'}).text.strip())
    ## PACE
    data['pace'] = stats[0]['pace'][0]['value']
    data['pace_acceleration'] = stats[0]['pace'][1]['value']
    data['pace_sprint_speed'] = stats[0]['pace'][2]['value']

    ## SHOOTING
    data['shooting'] = stats[0]['shooting'][0]['value']
    data['shoot_positioning'] = stats[0]['shooting'][1]['value']
    data['shoot_finishing'] = stats[0]['shooting'][2]['value']
    data['shoot_shot_power'] = stats[0]['shooting'][3]['value']
    data['shoot_long_shots'] = stats[0]['shooting'][4]['value']
    data['shoot_volleys'] = stats[0]['shooting'][5]['value']
    data['shoot_penalties'] = stats[0]['shooting'][6]['value']

    ## PASSING
    data['passing'] = stats[0]['passing'][0]['value']
    data['pass_vision'] = stats[0]['passing'][1]['value']
    data['pass_crossing'] = stats[0]['passing'][2]['value']
    data['pass_free_kick'] = stats[0]['passing'][3]['value']
    data['pass_short'] = stats[0]['passing'][4]['value']
    data['pass_long'] = stats[0]['passing'][5]['value']
    data['pass_curve'] = stats[0]['passing'][6]['value']


    ## DRIBBLING
    data['dribbling'] = stats[0]['dribbling'][0]['value']
    data['drib_agility'] = stats[0]['dribbling'][1]['value']
    data['drib_balance'] = stats[0]['dribbling'][2]['value']
    data['drib_reactions'] = stats[0]['dribbling'][3]['value']
    data['drib_ball_control'] = stats[0]['dribbling'][4]['value']
    data['drib_dribbling'] = stats[0]['dribbling'][5]['value']
    data['drib_composure'] = stats[0]['dribbling'][6]['value']

    ## DEFENDING
    data['defending'] = stats[0]['defending'][0]['value']
    data['def_interceptions'] = stats[0]['defending'][1]['value']
    data['def_heading'] = stats[0]['defending'][2]['value']
    data['def_marking'] = stats[0]['defending'][3]['value']
    data['def_stand_tackle'] = stats[0]['defending'][4]['value']
    data['def_slid_tackle'] = stats[0]['defending'][5]['value']

    ## PHYSICAL
    data['physicality'] = stats[0]['physical'][0]['value']
    data['phys_jumping'] = stats[0]['physical'][1]['value']
    data['phys_stamina'] = stats[0]['physical'][2]['value']
    data['phys_strength'] = stats[0]['physical'][3]['value']
    data['phys_aggression'] = stats[0]['physical'][4]['value']
    
    return data

def df_fetch_newplayers(player_id, dataframe):
    """
    Function used to add new players to our dataframe

    Arguments:
        player_id: The id of the latest player added on Futbin
        dataframe: Our dataframe
    
    Returns:
        dataframe: An updated dataframe with all the latest players and their data.
    """
    start_time = time()
    last_index = dataframe.index[-1]
    tot_players = player_id - last_index
    
    i = 0
    for player in range(last_index + 1, player_id + 1):
        try:
            stats = player_fetch_all(player)
            dataframe.loc[player] = stats
        except:
            print('No player found at ID: {}.'.format(player))
        i += 1
        if (i % 200 == 0) | (i == 1):
            print('Completed {} players. Time elapsed: {} seconds.'.format(i, 
                                                                           int(time() - start_time)))
            seconds_left = int((int(time() - start_time) / i) * (tot_players - i))
            print('Approximate time left: {} seconds.'.format(seconds_left))
    
    return dataframe


def df_fetch_price(dataframe):
    """
    Function used to fetch the prices for all players in a dataframe, and create another dataset with numerous entries for each player.
    An entry for every time-point.
    
    Arguments:
        dataframe: our original dataframe
        
    Returns:
        df_price: our new dataframe with the prices
    """
    resource_ids = dataframe['resource_id']
    prices = []
    tot_players = len(resource_ids)
    j = 0
    start_time = time()
    j_time = start_time
    last_j = 0
    for res_id in resource_ids:
        prices = player_fetch_price(res_id, prices)
        j += 1
        if (j % 200 == 0) | (j == 1):
            seconds_left = int(((int(time() - j_time)/(j-last_j)) * (tot_players - j)))
            print('Completed {} players. Time elapsed: {} seconds. Approx. {} seconds left.'.format(j, 
                                                                                                    int(time() - start_time), 
                                                                                                    seconds_left))
            j_time = time()
            last_j = j
    df_prices = pd.DataFrame(prices)
    df = dataframe.merge(df_prices, on = 'resource_id', how = 'right')
    return df

def player_fetch_price(res_id, prices):
    """
    Function used to find the prices for a particular player. 
    
    Arguments:
        res_id: an integer indicating a player's resource_id
        prices: a list containing dictionaries of prices, dates and resource_ids
        
    Returns:
        prices: the input dataframe updated with the new player's data
    """
    
    resp = requests.get('https://www.futbin.com/19/playerGraph?type=daily_graph&year=19&player=' + str(res_id))
    try:
        soup = BeautifulSoup(resp.text, 'html')
        price_data = json.loads(soup.text)['ps']
        for i in price_data:
            row = {'resource_id': res_id}
            row['date'] = strftime('%Y-%m-%d', localtime(i[0]/1000))
            row['price'] = i[1]
            prices.append(row)
    except:
        print('No prices available for player with the following resource_id: {}.'.format(res_id))
        
    return prices



def df_fetch_price_intervals(dataframe):
    """
    Identical function to df_fetch_price w/ breaks at every 1000 players.
    
    Arguments:
        dataframe: our original dataframe
        
    Returns:
        df_price: our new dataframe with the prices
    """
    resource_ids = dataframe['resource_id']
    prices = []
    tot_players = len(resource_ids)
    j = 0
    start_time = time()
    j_time = start_time
    last_j = 0
    for res_id in resource_ids:
        prices = player_fetch_price(res_id, prices)
        j += 1
        if (j % 200 == 0) | (j == 1):
            seconds_left = int(((int(time() - j_time)/(j-last_j)) * (tot_players - j)))
            print('Completed {} players. Time elapsed: {} seconds. Approx. {} seconds left.'.format(j, 
                                                                                                    int(time() - start_time), 
                                                                                                    seconds_left))
            if j % 1000 == 0:
                proceed = input('Proceed?')
                if proceed != 'y':
                    return df
            
            j_time = time()
            last_j = j
    df_prices = pd.DataFrame(prices)
    df = dataframe.merge(df_prices, on = 'resource_id', how = 'right')
    return df