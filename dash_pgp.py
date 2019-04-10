# Second plot, displaying the number of goals/assists/contributions for each
# player.
# Tick Buttons: Goal Assists
# Country Dropdown
# League Dropdown
# Position Dropdown

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('data/dash_groupedplayers_dataframe.csv', 
                 index_col='Unnamed: 0', parse_dates=['date', 'added_date'])

countries = df.nationality.unique()
leagues = df.league.unique()
positions = df.position.unique()

app.layout = html.Div([
    dcc.Graph(id='graph-with-dropdowns'),
    dcc.Dropdown(
        id='country',
        options=[{'label': i, 'value': i} for i in countries],
        value=None
    ),
    dcc.Dropdown(
        id='league',
        options=[{'label': i, 'value': i} for i in leagues],
        value=None
    ),
    dcc.Dropdown(
        id='position',
        options=[{'label': i, 'value': i} for i in positions],
        value=None
    ),
    dcc.RadioItems(
        id='contribution',
        options=[{'label': i, 'value': i} for i in ['Goals', 'Assists', 'Both']],
        value='Both',
        labelStyle={'display': 'inline-block'}
    ),
    dcc.RangeSlider(
        id='ratings',
        min=75,
        max=99,
        step=1,
        value=[84, 90],
        marks={str(overall): str(overall) for overall in df['overall'].unique()}
    )
])


@app.callback(
    Output('graph-with-dropdowns', 'figure'),
    [Input('country', 'value'),
     Input('league', 'value'),
     Input('position', 'value'),
     Input('contribution', 'value'),
      Input('ratings', 'value')])

def update_graph(country, league, position, contribution, ratings):
    df_ = df[(df.overall >= ratings[0]) & (df.overall <= ratings[1])]
    if country != None:
        df_ = df_[df_.nationality == country]
    if league != None:
        df_ = df_[df_.league == league]
    if position != None:
        df_ = df_[df_.position == position]
    if contribution == 'Both':
        x = 'avg_contributions'
        x_t = 'Average Number of Contributions'
    elif contribution == 'Goals':
        x = 'avg_goals'
        x_t = 'Average Number of Goals'
    else:
        x = 'avg_assists'
        x_t = 'Average Number of Assists'
    
    
    data =[]
    for res_id in df_.resource_id.unique():
        player_d = df_[df_.resource_id == res_id]
        data.append(go.Scatter(x=player_d[x],
                               y=player_d['price'],
                               mode='markers',
                               name=str(player_d.player_name.values[0]) + ' '+ str(player_d.overall.values[0]),
                               marker={
                                   'size': 10,
                                   'opacity': 0.5,
                                   'line': {'width': 0.5, 'color': 'blue'}
                               }
                    ))
        
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': x_t,
                'type': 'linear'
            },
            yaxis={
                'title': 'Price',
                'type': 'linear'
            },
            margin={'l': 40, 'b': 80, 't': 80, 'r': 40},
            hovermode='closest')
    }

if __name__ == '__main__':
    app.run_server(debug=True)