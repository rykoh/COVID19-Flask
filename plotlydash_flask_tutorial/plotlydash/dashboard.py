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



received = False



def create_dashboard(server):
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

    # Load DataFrame
    df = create_dataframe()

    dash_app.title = "COVID-19 Student Research Opportunities"

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

def generate_table(df):
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
    return table
    














