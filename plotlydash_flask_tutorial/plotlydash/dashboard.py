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

    dash_app.title = "COVID-19 Student Research Opportunities"

    # Load DataFrame
    df = create_dataframe()

    # Custom HTML layout
    dash_app.index_string = html_layout

    # Create Layout    get_input(), html.br()
    dash_app.layout = html.Div(
        children=[navbar(), html.Br(),
        # dcc.Graph(
        #     id='histogram-graph',
        #     figure={
        #         'data': [{
        #             'x': df['Key Words'],
        #             'text': df['Key Words'],
        #             'name': 'Research Categories',
        #             'type': 'histogram'
        #         }],
        #         'layout': {
        #             'title': 'Research Categories',
        #             'height': 500,
        #             'padding': 150
        #         }
        #     })
            create_data_table(df)
        ],
        id='dash-container'
    )

    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
    for i in range(0,df.shape[0]):
        dash_app.callback(
            Output(f"collapse{i}", "is_open"),
            [Input(f"collapse-button{i}", "n_clicks")],
            [State(f"collapse{i}", "is_open")],
        )(toggle_collapse)


    @dash_app.callback(Output('output_div', 'children'),
                  [Input('submit-button', 'n_clicks')],
                  [State('username', 'value')],
                  )
    def update_output(clicks, input_value):
        received = False
        if clicks is not None:
            client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/FlaskTable?retryWrites=true&w=majority")
            db = client.FlaskTable
            name = 'Feedback'
            collection = db[name]
            
            feedback = str(input_value)
           
            feedBackRaw = {'FeedbackVal': [feedback]}
            dataFrame = pd.DataFrame(data=feedBackRaw)
            dataFrame.reset_index(inplace=True)
            data_dict = dataFrame.to_dict("records")
            collection.insert_many(data_dict)
            received = True
            input_value = ''
            if received is True:
                return "\nWe got your feedback!"
            

    @dash_app.callback(
        [Output("modal", "is_open"), Output('output_div', 'is_open')],
        [Input("open", "n_clicks"), Input("close", "n_clicks")],
        [State("modal", "is_open"), State('username', 'value')],
    )
    def toggle_modal(n1, n2, is_open, value):

        received = False
        if n1 or n2:
            return not is_open, "Here"
        return is_open, "Here"
    return dash_app.server


def create_data_table(df):
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

    cardVal = dbc.CardColumns(allCards)
    tabs = dbc.Tabs(
    [
        dbc.Tab(cardVal, label="Card View"),
        dbc.Tab(table, label="Table View"),
    ]
    )
    return tabs

def get_input():
    inputFeed = html.Div(children = [
            dbc.Input(id='username', placeholder='Enter feedback here!',bs_size="lg", type='text'),
            html.Br(),
            dbc.Button( id='submit-button', children='Submit', style={'text-align':'center', 'width': '460px'}), 
            html.Div(id='output_div')
        ], style = {'width': '460px'})


    modal = html.Div(
        children = [
            dbc.Button("Give us feedback!", id="open"),
            dbc.Modal(
                [
                    dbc.ModalHeader("Enter your feedback down below!"),
                    dbc.ModalBody(inputFeed),
                    
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close", className="ml-auto")
                    ),
                ],
                id="modal",
            ),
        ], style = {'width': '150px'}
    )
    return modal

def navbar():
    # html.Header ? for a new header to be able to add the feedback form
    # use html div instead?? https://dash.plotly.com/dash-html-components/nav
    # make a reuseable navitem for the different examples
    # Try to include logo into this version of navbar
    # https://dash-bootstrap-components.opensource.faculty.ai/docs/components/navbar/
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(get_input()),
            dbc.NavItem(dbc.NavLink("Page 1", href="#")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("Page 2", href="#"),
                    dbc.DropdownMenuItem("Page 3", href="#"),
                ],
                nav=True,
                in_navbar=True,
                label="More",
            ),
        ],
        brand="COVID-19 Student Research Opportunities",
        brand_href="http://covid19research.herokuapp.com/",
        color="secondary",
        dark=True,
        style = {'height': '100px'}, # , 'margin-top': '-7.5%' fix the spacing on this including top margin and width using css style elements: https://www.w3schools.com/cssref/
        sticky = "top",
        fluid = True,
    )

    return navbar



