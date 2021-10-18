import dash 
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from whitenoise import WhiteNoise
import codes.dataset as dataset
import codes.callbacks as callbacks


external_stylesheets = [dbc.themes.SPACELAB]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/')

filename = 'static/UNdata_Export_20211018_063214641.csv'
energyData = dataset.EnergyData(filename)

# PRODUCTION - data
df_gen = callbacks.build_production_dataset(energyData=energyData, 
                                            year=2018, 
                                            transactions=['EP', 'SP', 
                                                          '015C', '016C',
                                                          '015HY', '016HY',
                                                          '015N', '016N',
                                                          '015W', '016W',
                                                          '015S', '016S',
                                                          '015H', '016H',
                                                          ], 
                                            codes=True)

# PRODUCTION - figures
fig_prod_bar = px.bar(df_gen[(df_gen['Purpose']!='Other') & (df_gen['Fuel']!='Total')], 
                      x='Fuel', y = 'Quantity (1e6 kW/h)', color='Purpose')
fig_prod_pie1 = px.pie(df_gen[(df_gen['Purpose']!='Other') & (df_gen['Fuel']!='Total')], 
             values = 'Quantity (1e6 kW/h)', names = 'Fuel', title = 'Total')
fig_prod_pie2 = px.pie(df_gen[(df_gen['Purpose'] == 'Main activity') & (df_gen['Fuel']!='Total')], 
             values = 'Quantity (1e6 kW/h)', names = 'Fuel', title = 'Main activity')
fig_prod_pie3 = px.pie(df_gen[(df_gen['Purpose'] == 'Autoproducer') & (df_gen['Fuel']!='Total')], 
             values = 'Quantity (1e6 kW/h)', names = 'Fuel', title = 'Autoproducer')


# CONSUMPTION - data
df_cons = callbacks.build_consumption_dataset(energyData=energyData,
                                              years = list(range(2008,2019)))

# CONSUMPTION - figures
fig_cons_line = px.line(df_cons, x='Year', y='Quantity (1e6 kW/h)', color='Consumer')
fig_cons_bar = px.bar(df_cons, x='Consumer', y = 'Quantity (1e6 kW/h)', color='Year', color_continuous_scale='oryel')

# create a dict of years and labels for the slider marks
year_map = {}
for year in energyData.data['Year'].unique():
    year_map[year] = str(year)
    
print(year_map)
    
# WORLD EXPLORER - data
df_world = callbacks.build_world_data(energyData, 2018, '12')
# WORLD EXPLORER - figures
fig_world = px.choropleth(data_frame=df_world, locations='ISO-3', locationmode='ISO-3', 
                          color='Quantity (1e6 kW/h)', color_continuous_scale='jet')

# APP LAYOUT
# ---------
# header
# ---------
# generation graphs: bar chart of absolute vals | pie chart with percentages, 
# callbacks: choose year
# ---------
# consumption graphs: line plot (x-year, y-consumption), bar chart with sum for all years
# callbacks: choose range of years
 
app.layout = dbc.Container([
    
    # header
    dbc.Container([
        html.H2('Electricity Generation and Consumption'),
        html.P('Exploration of data on total electricity from the UNDATA Energy Statistics Database (http://data.un.org/Explorer.aspx)')
    ], style={'margin': '0em', 'marginBottom': '1em', 'paddingBottom': '2em', 'paddingTop': '2em', 'backgroundColor': '#ffffff'}),
    
    # generation
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4(children='World Electricity Generation by Fuel'),
                html.P(children='Electricity generation by combustible fuels (coal, oil, natural gas),\
                         nuclear, solar, wind, hydro and chemical heat (biofuels).')
            ])
        ]),
        
        dbc.Row(
            dbc.Col([
                dcc.RadioItems(
                id='production-year',
                options=[{'label': i, 'value': i} for i in energyData.data['Year'].unique()],
                value=2018,
                labelStyle={'display': 'inline-block', 'margin': '5px'}
            )    
            ])
        ),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                id='production-bar',
                figure=fig_prod_bar
                )
                ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                id='production-pie1',
                figure=fig_prod_pie1
                )]),
            dbc.Col([
                dcc.Graph(
                id='production-pie2',
                figure=fig_prod_pie2
                )]),
            dbc.Col([
                dcc.Graph(
                id='production-pie3',
                figure=fig_prod_pie3
                )])
        ])
        
    ]),
    
    # consumption
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4(children='World Electricity Consumption by Sectors'),
                html.P(children='Electricity consumption by households, industry, transport, agriculture, \
                         and commercial / public services')
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.RangeSlider(
                    id='consumption-year-range',
                    min=energyData.data['Year'].min(),
                    max=energyData.data['Year'].max(),
                    step=None,
                    #TODO: debug why passing year_map fails
                    marks = { 
                             2018: '2018', 
                             2017: '2017', 
                             2016: '2016', 
                             2015: '2015', 
                             2014: '2014', 
                             2013: '2013', 
                             2012: '2012', 
                             2011: '2011', 
                             2010: '2010', 
                             2009: '2009', 
                             2008: '2008', 
                             2007: '2007', 
                             2006: '2006', 
                             2005: '2005', 
                             2004: '2004'}, 
                    value=[2008, 2018],
                    
                ),
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                id='consumption-line',
                figure=fig_cons_line
                )
                ]),
            dbc.Col([
                dcc.Graph(
                id='consumption-bar',
                figure=fig_cons_bar
                )
                ])
        ]),
                
    ]),
    
    
    # world explorer
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4(children='World Data Explorer'),
                html.P(children='Plot the energy per-country for a given year and transaction.')
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div(children='Year'),
                dcc.Dropdown(
                    id='world-data-year',
                    options=[{'label': i, 'value': i} for i in energyData.data['Year'].unique()],
                    value = 2018
                ),
            ]),
            dbc.Col([
                html.Div(children='Transaction'),
                dcc.Dropdown(
                    id='world-data-transaction',
                    options=[{'label': i, 'value': i} for i in energyData.data['Transaction'].unique()],
                    value = 'Final energy consumption'
                ),                
            ])
            ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                id='world-data',
                figure=fig_world
                )
                ])
        ]),
        
        dbc.Row([
            html.H5('Examples of questions we can answer with the World Explorer'),
            html.P('Which country was the highest producer of electricity via combustible fuels in 2018 vs 2008? '),
            html.P('Which countries were the top 3 consumers of electricity in 2018? How about 2005?'),
            html.P('Which countries import instead of produce most of their electricity? ')]),
        dbc.Row([
            html.H5('Questions we can answer from the dataset'),
            html.P('Are any countries likely to decrease their electricity production via combustible fuels \
                by at least 10% by 2028? '),
            html.P('Which country has seen the biggest rise in exported electricity in the decade of 2008-2018?')
            
            
        ])
        
    ])
    
])

# APP CALLBACKS

@app.callback(
    Output('production-bar', 'figure'),
    Output('production-pie1', 'figure'),
    Output('production-pie2', 'figure'),
    Output('production-pie3', 'figure'),
    [Input('production-year', 'value')]
)
def update_production_data(year):
    df_gen = callbacks.build_production_dataset(energyData=energyData, 
                                            year=year, 
                                            transactions=['EP', 'SP', 
                                                          '015C', '016C',
                                                          '015HY', '016HY',
                                                          '015N', '016N',
                                                          '015W', '016W',
                                                          '015S', '016S',
                                                          '015H', '016H',
                                                          ], 
                                            codes=True)
    
    fig_prod_bar = px.bar(df_gen[(df_gen['Purpose']!='Other') & (df_gen['Fuel']!='Total')], 
                        x='Fuel', y = 'Quantity (1e6 kW/h)', color='Purpose')
    fig_prod_pie1 = px.pie(df_gen[(df_gen['Purpose']!='Other') & (df_gen['Fuel']!='Total')], 
                values = 'Quantity (1e6 kW/h)', names = 'Fuel', title = 'Total')
    fig_prod_pie2 = px.pie(df_gen[(df_gen['Purpose'] == 'Main activity') & (df_gen['Fuel']!='Total')], 
                values = 'Quantity (1e6 kW/h)', names = 'Fuel', title = 'Main activity')
    fig_prod_pie3 = px.pie(df_gen[(df_gen['Purpose'] == 'Autoproducer') & (df_gen['Fuel']!='Total')], 
                values = 'Quantity (1e6 kW/h)', names = 'Fuel', title = 'Autoproducer')
    
    return fig_prod_bar, fig_prod_pie1, fig_prod_pie2, fig_prod_pie3


@app.callback(
    Output('consumption-line', 'figure'),
    Output('consumption-bar', 'figure'),
    [Input('consumption-year-range', 'value')]
)
def update_consumption_data(year_range):
    df_cons = callbacks.build_consumption_dataset(energyData=energyData,
                                              years = list(range(year_range[0],year_range[1]+1)))

    # CONSUMPTION - figures
    fig_cons_line = px.line(df_cons, x='Year', y='Quantity (1e6 kW/h)', color='Consumer')
    fig_cons_bar = px.bar(df_cons, x='Consumer', y = 'Quantity (1e6 kW/h)', color='Year', color_continuous_scale='oryel')
    return fig_cons_line, fig_cons_bar
    
    
@app.callback(
    Output('world-data', 'figure'),
    [Input('world-data-year', 'value'),
     Input('world-data-transaction', 'value'),
     ]
)
def update_world_data(year, transaction):
    df_world = callbacks.build_world_data(energyData, year, energyData.transaction_map[transaction])
    return px.choropleth(data_frame=df_world, locations='ISO-3', locationmode='ISO-3', 
                         color='Quantity (1e6 kW/h)', color_continuous_scale='jet')
    

if __name__ == '__main__':
    app.run_server(debug=True)