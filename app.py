#flask and dash together
from flask import Flask, render_template
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import json
import requests
import pandas as pd
from pandas import json_normalize
import dash_table
import os
import sys
from backend import parserFuncs

server = Flask(__name__)
@server.route('/flask')
def index():

    return 'hello'
    

app = Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/'
)

#this is the array set up for the drop down year
year_options = [i for i in range(1992, 2020)]

#to generate table for Match Stats
def generate_match_stats(dataframe):
    match_stats_table = html.Div([
            html.H3('Match Stats'),
            dash_table.DataTable(
                id = 'match_stats_data_table',
                columns = [{"name": i, "id": i} for i in dataframe.columns],
                data = dataframe.to_dict('records')
            )
        ])
    return match_stats_table

#create the layout
app.layout =html.Div([
    html.H1('Blue Alliance Data', style = {
        'textAlign': 'center'
    }),
    #first drop-down for year
    html.Label(["Please select a year",
    dcc.Dropdown(
        id = 'year-dropdown',
        options=[
           {'label': k, 'value': k} for k in year_options
           
        ]
    )]),

    #second drop-down for event location
    html.Label(id = 'event-label', style = {'visibility': 'hidden'}, children = ["Please select an event",
    dcc.Dropdown(
        id = 'event-dropdown',
        options=[]
    )]),

    #Drop down for reports 
   html.Label(id = 'multiselect-reports-label', style = {'visibility': 'hidden'}, children = ["Please select a report from the list",
    dcc.Dropdown(
        id = 'report-dropdown',
        options=[
            {'label': 'Average Stats by Team', 'value': 'Average Stats by Team'},
            {'label': 'Match Stats', 'value': 'Match Stats'},
            {'label': 'Draft Simulator', 'value': 'Draft Simulator'},
            {'label': 'Rank Model', 'value': 'Rank Model'},
            {'label': 'Elimination Simulator', 'value': 'Elimination Simulator'}
        ],
        multi = True
    )]), 
    #tabs to diplsay report

    html.Div(id = 'tab-options', style = {'visibility': 'hidden'},\
        children = [dcc.Tabs(id = 'tabs-reports', children= [])]),
    
    html.Div(id = 'tab-content-averageStats', style = {'visibility': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}),

    html.Div(id = 'tab-content-matchStats', style = {'visibility': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}, children = [html.Label(id = 'match-StatsLabel', children = ["Please select data to display",
    dcc.Dropdown(
        id = 'matchStats-dropdown',
        options=[],
        multi = True
    )]),
    html.Button('submit table updates', id ='matchStats-submit'),
    html.Div(id = 'matchStats-table', children = [])]),

    html.Div(id = 'tab-content-draftSimulator', style = {'visibiity': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}),

    html.Div(id = 'tab-content-rankModel', style = {'visibility': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}),

    html.Div(id = 'tab-content-eliminationSimulator', style = {'visibility': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}),

    #for outputs, 
    html.Div(id = 'output-container', children = [])
    #html.Div(id='dd-output-container')
])

@app.callback(
    #Output('dd-output-container', 'children'),
    [Output('event-label', 'style'), Output('event-dropdown', 'options')],
    [Input('year-dropdown', 'value')]
    #[State('dropdown-container', 'children')]
)

def display_dropdown(year):
    eventStyle = {'visibility': 'hidden'}
    city_States = []

    if not (year is None):
        eventStyle = {'visibility': 'visible'}
        
        #Authentication Code for BlueAlliance API
        headers = {'X-TBA-Auth-Key' : '3BFWLXdBe4yJUCo73Ky3hiBLdKNwCWHe9Nm1Xwr3JSIv5oOM3S1UNdufyTMKBAVU'}
    
        #Pull list of events for a specific year
        r = requests.get('https://www.thebluealliance.com/api/v3/events/' + str(year), headers = headers)
        
        events_dump = r.json()

        #Extracting the desired data into a list: city, state_prov, event
        for event in events_dump:
            if not(event['city'] is None):
                city_States.append({'label': event['name']+ ', ' +event['city']+', ' +event['state_prov'], 'value':event['key']})

    
    return eventStyle, city_States

@app.callback(
    Output('multiselect-reports-label', 'style'),
    [Input('event-dropdown', 'value')]
)

def display_reports_dropdown(city_event):
    reportsStyle = {'visibility': 'hidden'}

    if not(city_event is None):
        reportsStyle = {'visibility': 'visible'}
    
    return  reportsStyle

#separate app callback for tabs report content, make style visible
#if that tab is selected then show the content for that tab
#Output('tab-options', 'children')

@app.callback(
    [Output('tab-options', 'style'), Output('tabs-reports', 'children')],
    [Input('report-dropdown', 'value')]
)

#Creates the tab from the multi-select drop-down
def display_tab(tab_triggered):

    tabStyle = {'visibility': 'hidden'}
    tab_report_name = []

    if not(tab_triggered is None):

        for x in tab_triggered:
            tab_report_name.append(dcc.Tab(label =  x, value = x))

        tabStyle = {'visibility': 'visible'}
        
    return tabStyle, tab_report_name


@app.callback(
    [Output('tab-content-averageStats', 'children'), Output('tab-content-averageStats', 'style'), Output('matchStats-dropdown', 'options'), Output('tab-content-matchStats', 'style'),
    Output('tab-content-draftSimulator','children'), Output('tab-content-draftSimulator', 'style'), Output('tab-content-rankModel', 'children'),
    Output('tab-content-rankModel', 'style'),Output('tab-content-eliminationSimulator', 'children'), Output('tab-content-eliminationSimulator', 'style')],
    [Input('tabs-reports', 'value'), Input('event-dropdown', 'value')])

#Dictates which content will be displayed
def display_tab_content(tab, key):
    
    api_key = '3BFWLXdBe4yJUCo73Ky3hiBLdKNwCWHe9Nm1Xwr3JSIv5oOM3S1UNdufyTMKBAVU'

    averageStatsStyle = {'visibility': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}
    matchStatsStyle = {'visibility': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}
    draftSimulatorStyle = {'visibility': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}
    rankModelStyle = {'visibility': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}
    eliminationSimulatorStyle = {'visibility': 'hidden', 'height': '0px', 'padding-bottom': '0px', 'padding-top': '0px', 'padding-left': '0px'}
    contentAveStats = []
    contentDraftSim = []
    contentRankModel = []
    contentEliminationSim = []
    matchStatsoptions = []

    if tab == 'Average Stats by Team':
        averageStatsStyle = {'visibility': 'visible'}
        contentAveStats = html.Div([
            html.H3('Average Stats By Team')
        ])
    
    elif tab == 'Match Stats':
        #Getting the list of things, FRC match function, with event key: obtain data frame
        #make seperate empty content for html things to include drop down
        matchStatsStyle = {'visibility': 'visible'}
        match_stats_df = pd.DataFrame()
        
        try:
            match_stats_df = parserFuncs.frc_matchData(key, api_key)
        except:
            matchStatsoptions.append({'label': 'no data available', 'value': ""})
        
        if not (match_stats_df.empty):

            for col in match_stats_df:
                if all([col != 'blue1', col != 'blue2', col != 'blue3', col != 'red1', col != 'red2', col != 'red3']):
                    matchStatsoptions.append({'label': col, 'value': col})


    elif tab == 'Draft Simulator':
        draftSimulatorStyle = {'visibility': 'visible'}
        contentDraftSim = html.Div([
            html.H3('Draft Simulator')
        ])
    
    elif tab == 'Rank Model':
        rankModelStyle = {'visibility': 'visible'}
        contentRankModel = html.Div([
            html.H3('Rank Model')
        ])
    
    elif tab == 'Elimination Simulator':
        eliminationSimulatorStyle = {'visibility': 'visible'}
        contentEliminationSim = html.Div([
            html.H3('Elimination Simulator')
        ])

    return contentAveStats, averageStatsStyle, matchStatsoptions, matchStatsStyle, contentDraftSim, draftSimulatorStyle, contentRankModel, rankModelStyle, contentEliminationSim, eliminationSimulatorStyle

@app.callback(
    Output('matchStats-table', 'children'),
    [Input('matchStats-submit', 'n_clicks'), Input('matchStats-dropdown', 'value'), Input('event-dropdown', 'value')])


def update_matchStats_table(n_clicks, multi_choices, eventKey):
    api_key = '3BFWLXdBe4yJUCo73Ky3hiBLdKNwCWHe9Nm1Xwr3JSIv5oOM3S1UNdufyTMKBAVU'
    df = pd.DataFrame()
    updated_table = []
    error_output = []
    if n_clicks is None:
        raise PreventUpdate
    elif (multi_choices == "") or (multi_choices is None):
        error_output = html.Div([
            html.H3('Please select a value')
        ])
        return error_output
    else:
        try:
            df = parserFuncs.frc_matchData(eventKey, api_key)
        except:
            raise PreventUpdate
        if not (df.empty):
            col_list = ["blue1", "blue2", "blue3", "red1", "red2", "red3"] + multi_choices
            updated_table = generate_match_stats(df.loc[:,col_list])
            #updated_table = generate_match_stats(df)
            return updated_table

        #dff = df[df.state.str.contains('|'.join(dropdown_value))]

if __name__ == '__main__':
    app.run_server(debug=True)