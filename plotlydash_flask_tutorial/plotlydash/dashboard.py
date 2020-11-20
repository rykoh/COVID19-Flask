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

# Fucntion to generate the table
def generate_table(df, max_rows=100000):
    """
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
    # add css
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))]
    )

    allCards = []

    for index, row in df.iterrows():

        source = "Source: " +row["Data Source"]
        titleCoord = "Project Title/Coordinator: "+row["Project Title/ Coordinator"]
        keyWrd = "Area of Interest: "+row["Key Words"]
        typeRes = "Type of Research: "+row["Type of Research"]
        descVal = "Description: "+row["Description"]
        contact = "Relevant Links/Point of Contact: "+row["Relevant Links/POC"]
        

        currCard = dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H5(source, className="card-title"),
                    html.P(
                        titleCoord,
                        className="card-text",
                    ),
                    html.P(
                        keyWrd,
                        className="card-text",
                    ),
                    html.H2(
                    dbc.Button(
                        "Click here for more!",
                        id=f"collapse-button{index}",
                    )
                )
                ]
            ),
            dbc.Collapse(
                dbc.CardBody([html.P(
                        typeRes,
                        className="card-text",
                    ),html.P(
                        descVal,
                        className="card-text",
                    ),html.P(
                        contact,
                        className="card-text",
                    )]),
                id=f"collapse{index}",
            ),
        ]
        )
        allCards.append(currCard)

    cardVal = dbc.CardColumns(allCards, id = "cardcolumns")
    tabs = dbc.Tabs(
    [
        dbc.Tab(cardVal, label="Card View"),
        dbc.Tab(table, label="Table View"),
    ]
    )

    final = html.Div(tabs)
    return final


# Main Function
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

    # Callback for table
    @dash_app.callback(
        dash.dependencies.Output('database-table', 'children'),
        [dash.dependencies.Input('Sources', 'value')])
    def display_table(dropdown_value):
        if dropdown_value == []:
            return generate_table(df)

        
        # print(dropdown_value) [{'label': 'UT Austin', 'value': 'UT Austin'}, {'label': 'Stanford', 'value': 'Stanford'}, {'label': 'Virginia Tech', 'value': 'Virginia Tech'}]
        # print(type(dropdown_value)) <class 'list'>
    
        #dff = df[df["Data Source"].str.contains('|'.join(dropdown_value))]
        indicators = []
        for selector in dropdown_value:

            if isinstance(selector, dict):
                category = selector['value']
                indicators.append(category)
            else:
                indicators.append(selector)
                
        result = df[df['Data Source'].isin(indicators)]
        return generate_table(result)


    return dash_app.server



    














