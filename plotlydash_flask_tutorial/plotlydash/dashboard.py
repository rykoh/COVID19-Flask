"""Instantiate a Dash app."""
import numpy as np
import pandas as pd
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from .data import create_dataframe
from .layout import html_layout
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from pymongo import MongoClient


def generate_table(df, max_rows=10):
    
    table = dash_table.DataTable(
            id='database-table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            sort_action="native",
            sort_mode='native',
            style_table={'overflowX': 'scroll', 'overflowY': 'scroll', 'padding': '2px 22px',},
            style_cell={"whiteSpace": "normal", "height": "auto", 'textAlign': 'left'},
            page_size=300  
    )
    
    """
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))]
    )
    """

    return table

def create_dashboard(server):

    received = False

    # Load DataFrame
    df = create_dataframe()

    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
            'https://fonts.googleapis.com/css?family=Lato',
            dbc.themes.BOOTSTRAP
        ]
    )
    
    # Custom HTML layout
    dash_app.index_string = html_layout

    # Create Layout    get_input(), html.br()
    dash_app.layout = html.Div(
        children=[html.Br(), 

        html.Div(children = [

            html.H5('Source:'),

            dcc.Dropdown(
                id = 'Sources',
                options=[
                        {'label': i, 'value': i} for i in df["Data Source"].unique()
                    ],
                multi=True,
                value=[{'label': i, 'value': i} for i in df["Data Source"].unique()],
                ),

            html.Br(),

            html.H5('Area of Interest:'),

            dcc.Dropdown(
                id = 'Interests',
                options=[
                        {'label': i, 'value': i} for i in df["Key Words"].unique()
                    ],
                multi=True,
                value=[{'label': i, 'value': i} for i in df["Key Words"].unique()],
            ),

        html.Br(),

        html.Br(),
        ]),

        html.Div(id='database-table')
        ],
        id='dash-container'
    )

    @dash_app.callback(
        dash.dependencies.Output('database-table', 'children'),
        [dash.dependencies.Input('Sources', 'value')])
    def display_table(dropdown_value):
        if dropdown_value == []:
            return generate_table(df)

        
        # print(dropdown_value) [{'label': 'UT Austin', 'value': 'UT Austin'}, {'label': 'Stanford', 'value': 'Stanford'}, {'label': 'Virginia Tech', 'value': 'Virginia Tech'}]
        # print(type(dropdown_value)) <class 'list'>
    
        #dff = df[df["Data Source"].str.contains('|'.join(dropdown_value))]
        """
        dff = generate_table(df)
        my_list = []
        for dic in dropdown_value:
            print(dic)
            filt_keys = ['value'] 
            print(filt_keys)
            res = [dic[key] for key in filt_keys]
            print(res)
            var = res[0]
            print(var)
            my_list.append(var)
        print(my_list)

        # Filter the df for rows where df data source is in my_list
        print(dff['Data Source'])
        filtered_df = dff[dff["Data Source"] ]

        return generate_table(filtered_df)
        """

    return dash_app.server



    














