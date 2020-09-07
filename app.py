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

# This is the array set up for the drop down year
year_options = [i for i in range(1992, 2020)]

# Create the layout
app.layout =html.Div(className='dash-bootstrap',\
                     children=[html.Link(id='dark_theme',\
                                         rel='stylesheet',\
                                         href='/static/dark-dash.css',\
                                         title='Darkly'),\
                               html.H1('FRC Data Analytics', style = {'textAlign': 'center'}),\
                               html.H2(html.U('Options'), style = {'textAlign': 'left'}),\
                               # First drop-down for year
                               html.Div(id='year-div',\
                                        style={'padding-bottom':'10px',\
                                               'padding-top':'10px',\
                                               'padding-left': '0px',\
                                               'text-align':'left',\
                                               'width':'600px'},\
                                        children=[html.Div(id='year-label',\
                                                           children=[html.B(children='Year:',\
                                                                            style={'font-size':'20px'})],\
                                                           style={'display':'inline-block',\
                                                                  'width':'100px',\
                                                                  'vertical-align':'top'}),\
                                                  dcc.Dropdown(id='year-dropdown',\
                                                               options=[{'label': k, 'value': k} for k in year_options],\
                                                               style={'display': 'inline-block',\
                                                                      'min-width':'100px'})]),\

                               # Second drop-down for event location
                               html.Div(id='event-div',\
                                        style={'visibility':'hidden'},\
                                        children=[html.Div(id='event-label',\
                                                           children=[html.B('Event:',\
                                                                            style={'font-size':'20px'})],\
                                                           style={'display':'inline-block',\
                                                                  'width':'100px',\
                                                                  'vertical-align':'top'}),\
                                                  dcc.Dropdown(id = 'event-dropdown',\
                                                               options=[],\
                                                               style={'display': 'inline-block',\
                                                                      'min-width':'700px'})]),
                               
                               # Drop down for reports
                               html.Div(id='multiselect-reports-label',\
                                        style={'visibility':'hidden'},\
                                        children=[html.Div(id='report-label',\
                                                           children=[html.B('Reports:',\
                                                                            style={'font-size':'20px'})],\
                                                           style={'display':'inline-block',\
                                                                  'width':'100px',\
                                                                  'vertical-align':'top'}),\
                                                dcc.Dropdown(id='report-dropdown',\
                                                             options=[{'label': 'Average Stats by Team', 'value': 'Average Stats by Team'},\
                                                                      {'label': 'Match Stats', 'value': 'Match Stats'},\
                                                                      {'label': 'Draft Simulator', 'value': 'Draft Simulator'},\
                                                                      {'label': 'Rank Model', 'value': 'Rank Model'},\
                                                                      {'label': 'Elimination Simulator', 'value': 'Elimination Simulator'}],\
                                                             multi = True,\
                                                             style={'display': 'inline-block',\
                                                                    'min-width':'250px'})]),\
                               
                               # Tabs to display report
                               html.Div(id='tab-options',\
                                        style={'visibility': 'hidden'},\
                                        children=[dcc.Tabs(id = 'tabs-reports',\
                                                           children= [])]),\
                               html.Div(id='tab-content-averageStats',\
                                        style={'visibility':'hidden'}),\
                               html.Div(id='tab-content-matchStats',\
                                        style={'visibility':'hidden'},\
                                        children=[html.Div(id='match-StatsLabel',
                                                           children=[html.B('Columns:',\
                                                                            style={'font-size':'20px'})],\
                                                           style={'display':'inline-block',\
                                                                  'width':'100px',\
                                                                  'vertical-align':'top'}),\
                                                  dcc.Dropdown(id = 'matchStats-dropdown',\
                                                               options=[],\
                                                               multi = True,\
                                                               style={'display':'inline-block',\
                                                                      'min-width':'300px',\
                                                                      'vertical-align':'top'}),\
                               html.Div(id='matchStats-table',\
                                        children=[])]),\
                               html.Div(id='tab-content-draftSimulator',\
                                        style={'visibiity':'hidden'}),\
                               html.Div(id='tab-content-rankModel',\
                                        style={'visibility':'hidden'}),\
                               html.Div(id='tab-content-eliminationSimulator',\
                                        style={'visibility':'hidden'}),\

                               # For output div
                               html.Div(id='submit-div',\
                                        style={'visibility':'hidden'},\
                                        children=[html.Button('Submit',\
                                                              id='submit')]),\
                               html.Div(id='output-container',\
                                        style={'visibility':'hidden'},\
                                        children=[])])

#############################################################################
# Variables that will change when connected to backend (Blue Alliance)
api_key = '3BFWLXdBe4yJUCo73Ky3hiBLdKNwCWHe9Nm1Xwr3JSIv5oOM3S1UNdufyTMKBAVU'
headers = {'X-TBA-Auth-Key':api_key}
#############################################################################

@app.callback([Output('event-div', 'style'),\
               Output('event-dropdown', 'options')],\
              [Input('year-dropdown', 'value')])
def display_dropdown(year):
    eventStyle = {'visibility': 'hidden'}
    city_States = []

    if not (year is None):
        eventStyle ={'visibility': 'visible',\
                     'padding-bottom':'10px',\
                     'padding-top':'10px',\
                     'padding-left': '0px',\
                     'text-align':'left',\
                     'width':'800px'}
    
        #Pull list of events for a specific year
        r = requests.get('https://www.thebluealliance.com/api/v3/events/' + str(year), headers = headers)
        
        events_dump = r.json()

        #Extracting the desired data into a list: city, state_prov, event
        for event in events_dump:
            if not(event['city'] is None):
                city_States.append({'label': event['name']+ ' (' +event['city']+', ' +event['state_prov']+')', 'value':event['key']})

    return eventStyle, city_States

@app.callback(Output('multiselect-reports-label', 'style'),\
              [Input('event-dropdown', 'value')])
def display_reports_dropdown(city_event):
    reportsStyle = {'visibility': 'hidden'}

    if not(city_event is None):
        reportsStyle = {'padding-bottom':'10px',\
                        'padding-top':'10px',\
                        'padding-left': '0px',\
                        'text-align':'left',\
                        'min-width':'350px'}
    
    return  reportsStyle

# Separate app callback for tabs report content
# Makes style visible if that tab is selected then show the content for that tab
# Creates the tab from the multi-select drop-down
@app.callback([Output('tab-options', 'style'),\
               Output('tabs-reports', 'children')],\
              [Input('report-dropdown', 'value')])
def display_tab(tab_triggered):

    tabStyle = {'visibility':'hidden'}
    tab_report_name = []

    if not(tab_triggered is None):
        
        tabsWidth = 0
        for x in tab_triggered:
            tab_report_name.append(dcc.Tab(label=x, value=x, style={'width':'200px','height':'20px'}))
            tabsWidth += 200
        
        tabStyle = {'visibility': 'visible',\
                    'width':str(tabsWidth)+'px'}
        
    return tabStyle, tab_report_name

@app.callback([Output('submit-div','style'),\
               Output('tab-content-averageStats','children'),\
               Output('tab-content-averageStats','style'),\
               Output('matchStats-dropdown','options'),\
               Output('tab-content-matchStats','style'),\
               Output('tab-content-draftSimulator','children'),\
               Output('tab-content-draftSimulator','style'),\
               Output('tab-content-rankModel','children'),\
               Output('tab-content-rankModel','style'),\
               Output('tab-content-eliminationSimulator','children'),\
               Output('tab-content-eliminationSimulator','style')],
              [Input('tabs-reports','value'),\
               Input('event-dropdown','value')])

#Dictates which content will be displayed
def display_tab_content(tab, key):
    # Submit button style
    submitStyle = {'visibility':'hidden',\
                   'height':'0px',\
                   'padding-bottom':'0px',\
                   'padding-top':'0px',\
                   'padding-left':'0px'}

    # Report sub-menu styles
    averageStatsStyle = {'visibility':'hidden',\
                         'height':'0px',\
                         'padding-bottom':'0px',\
                         'padding-top':'0px',\
                         'padding-left':'0px'}
    matchStatsStyle = {'visibility':'hidden',\
                       'height':'0px',\
                       'padding-bottom':'0px',\
                       'padding-top': '0px',\
                       'padding-left': '0px'}
    draftSimulatorStyle = {'visibility':'hidden',\
                           'height':'0px',\
                           'padding-bottom':'0px',\
                           'padding-top':'0px',
                           'padding-left':'0px'}
    rankModelStyle = {'visibility':'hidden',\
                      'height':'0px',\
                      'padding-bottom':'0px',\
                      'padding-top':'0px',\
                      'padding-left':'0px'}
    eliminationSimulatorStyle = {'visibility':'hidden',\
                                 'height':'0px',\
                                 'padding-bottom':'0px',\
                                 'padding-top': '0px',\
                                 'padding-left': '0px'}
    
    # Report Content
    contentAveStats = []
    contentDraftSim = []
    contentRankModel = []
    contentEliminationSim = []
    matchStatsoptions = []

    if (not(tab is None)) & (tab != 'tab-1'):
        submitStyle = {'visibility':'visible',\
                        'height':'10px',\
                        'padding-bottom':'10px',\
                        'padding-top':'10px',\
                        'padding-left':'0px'}

    if tab == 'Average Stats by Team':        
        averageStatsStyle = {'visibility':'visible'}
        contentAveStats = html.Div([html.H3('Average Stats By Team')])
    
    elif tab == 'Match Stats':
        # Getting the list of things, FRC match function, with event key: obtain data frame
        # make seperate empty content for html things to include drop down
        matchStatsStyle = {'visibility':'visible',\
                           'padding-bottom':'10px',\
                           'padding-top':'10px',\
                           'padding-left':'0px',\
                           'min-width':'400px'}
        match_stats_df = pd.DataFrame()
        
        try:
            match_stats_df = parserFuncs.frc_matchData(key, api_key)
        except:
            matchStatsoptions.append({'label': 'no data available', 'value': ''})
        
        if not (match_stats_df.empty):

            for col in match_stats_df:
                if not (col in ['blue1','blue2','blue3','red1','red2','red3']):
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

    return submitStyle, contentAveStats, averageStatsStyle, matchStatsoptions, matchStatsStyle, contentDraftSim, draftSimulatorStyle, contentRankModel, rankModelStyle, contentEliminationSim, eliminationSimulatorStyle

# Callback for match statistics report
@app.callback([Output('output-container','children'),\
               Output('output-container','style')],\
              [Input('submit','n_clicks')],\
              [State('matchStats-dropdown','value'),\
               State('event-dropdown','value')])

def update_matchStats_table(n_clicks,\
                            multi_choices,\
                            eventKey):
    
    outputStyle = {'visibility':'hidden',\
                   'padding-bottom':'0px',\
                   'padding-top':'0px',\
                   'padding-left':'0px'}
    
    df = pd.DataFrame()
    output = []
    
    if n_clicks is None:
        raise PreventUpdate
    
    if multi_choices:
        try:
            df = parserFuncs.frc_matchData(eventKey, api_key)
        except:
            raise PreventUpdate
        
        if not df.empty:
            outputStyle = {'visibility':'visible',\
                           'padding-bottom':'10px',\
                           'padding-top':'10px',\
                           'padding-left':'0px'}
            col_list = ['blue1','blue2','blue3','red1','red2','red3'] + multi_choices
            updated_table = generate_table(df.loc[:,col_list],'matchStats')

            output = updated_table
            
    else:
        outputStyle = {'visibility':'visible',\
                       'padding-bottom':'10px',\
                       'padding-top':'10px',\
                       'padding-left':'0px'}
        error_output = html.Div(id='error-div',\
                                children=[html.B('Please select a column value',\
                                                 style={'font-size':'20px',\
                                                        'color':'red'})],\
                                style={'padding-bottom':'10px',\
                                       'padding-top':'10px',\
                                       'padding-left':'0px'})
        output = error_output
    
    return output,outputStyle




# General Functions (NOT callbacks)
#############################################################################################

# Generate table
def generate_table(dataframe,divID):
    match_stats_table = html.Div(id=divID+'-div',\
                                 style={'padding-bottom':'10px',\
                                        'padding-top':'10px',\
                                        'padding-left':'0px'},\
                                 children=[html.B('Match Stats',\
                                                  style={'font-size':'40px'}),\
                                           dash_table.DataTable(id = divID+'-table',\
                                                                columns = [{'name': i, 'id': i} for i in dataframe.columns],\
                                                                data = dataframe.to_dict('records'))])
    
    return match_stats_table

if __name__ == '__main__':
    app.run_server(debug=True)