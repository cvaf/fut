import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('data/dash_players_dataframe.csv', 
                 index_col='Unnamed: 0', parse_dates=['date', 'added_date'])

flashback_players = df[df.revision == 'Flashback SBC'].player_name.unique()

app.layout = html.Div([
    dcc.Graph(id='graph-with-dropdowns'),
    dcc.Dropdown(
        id='player-type',
        options=[{'label': i, 'value': i} for i in flashback_players],
        value='Mario Götze'
    ),
    dcc.RadioItems(
        id='link-type',
        options=[{'label': i, 'value': i} for i in ['Perfect', 'Strong', 'Weak']],
        value='Strong',
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Slider(
        id='numplayers--slider',
        min=1,
        max=10,
        value=5,
        marks={str(num): str(num) for num in range(1, 11)}
    )
])

@app.callback(
    dash.dependencies.Output('graph-with-dropdowns', 'figure'),
    [dash.dependencies.Input('player-type', 'value'),
     dash.dependencies.Input('link-type', 'value'),
     dash.dependencies.Input('numplayers--slider', 'value')])

def update_graph(player, link_type, num_players):
    # getting the player's attributes
    df_p = df[(df.player_name == player) & (df.revision == 'Flashback SBC')].iloc[0]
    nat = df_p.nationality
    club = df_p.club
    date = df_p.added_date
    league = df_p.league
    
    
    # filtering for the appropriate link type
    if link_type == 'Perfect':
        comp_data = df[(df.club == club) & (df.nationality == nat)]
    elif link_type == 'Strong':
        comp_data = df[(df.club == club) | ((df.league == league) & (df.nationality == nat))]
    elif link_type == 'Weak':
        comp_data = df[(df.nationality == nat) | (df.league == league)]
    
    # filtering for the appropriate dates
    comp_data = comp_data[(comp_data.date > date - timedelta(3)) & 
                          (comp_data.date < date + timedelta(3))]
    
    # removing 0 prices
    comp_data = comp_data[comp_data.price != 0]
    
    # removing the player's own data
    comp_data = comp_data[comp_data.player_name != player]

    comp_data['rel_day'] = np.nan
    for i in range(-2,3):
        comp_data['rel_day'] = np.where(comp_data.date == date - timedelta(i), 
                                        -i, comp_data.rel_day)

    # filtering for the number of players we are interested in
    comp_data.sort_values(by='overall', ascending=False, inplace=True)
    comp_players = comp_data.resource_id.unique()[:num_players]
    comp_data = comp_data[comp_data.resource_id.isin(comp_players)]
    comp_players_names = {}
    for i in comp_players:
        comp_players_names[i] = comp_data[comp_data.resource_id == i].player_name.unique()[0] + ' ' + str(comp_data[comp_data.resource_id == i].overall.unique()[0])
    
    data = []
    for i in comp_players:
        comp_data_s = comp_data[comp_data.resource_id == i]
        comp_data_s.sort_values(by='rel_day', ascending=True, inplace=True)
        data.append(go.Scatter(
                    x=comp_data_s.rel_day,
                    y=comp_data_s.price,
                    mode='lines+markers',
                    name= comp_players_names[i],
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
                'title': 'Days from Flashback Player release',
                'type': 'linear'
            },
            yaxis={
                'title': 'Price',
                'type': 'linear'
            },
            margin={'l': 40, 'b': 80, 't': 80, 'r': 40},
            hovermode='closest'
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)

    