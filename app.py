#flask and dash together
from flask import Flask, render_template

from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context
import dash_table

import json
import requests
import numpy as np
import pandas as pd
from pandas import json_normalize
import urllib
import time
import os
import sys

from backend import parserFuncs
#from backend import tgParserFuncs
from backend import teamStatFuncs
from backend import teamPlotFuncs

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
                                                  html.Div(id='year-dropdown-div',\
                                                           children=[dcc.Dropdown(id='year-dropdown',\
                                                                     options=[{'label': k, 'value': k} for k in year_options])],\
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
                                                  html.Div(id='event-dropdown-div',\
                                                           children=[dcc.Dropdown(id='event-dropdown',\
                                                                                  options=[])],\
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
                                                  html.Div(id='report-dropdown-div',\
                                                           children=[dcc.Dropdown(id='report-dropdown',\
                                                                                  options=[{'label': 'Average Stats by Team', 'value': 'Average Stats by Team'},\
                                                                                           {'label': 'Match Stats', 'value': 'Match Stats'},\
                                                                                           {'label': 'Draft Simulator', 'value': 'Draft Simulator'},\
                                                                                           {'label': 'Rank Model', 'value': 'Rank Model'},\
                                                                                           {'label': 'Elimination Simulator', 'value': 'Elimination Simulator'}],\
                                                                                  multi = True)],\
                                                           style={'display': 'inline-block',\
                                                                  'min-width':'250px'})]),\
                               
                               # Tabs to display report
                               html.Div(id='tab-options',\
                                        style={'visibility': 'hidden'},\
                                        children=[dcc.Tabs(id = 'tabs-reports',\
                                                           children= [])]),\
                               
                               html.Div(id='tab-content-averageStats',\
                                        style={'visibility':'hidden'},\
                                        children=[html.Div(id='averageStats-teams',\
                                                           style={'width':'300px'},\
                                                           children=[html.Div(id='teamsLabel',\
                                                                              children=[html.B('Teams:',\
                                                                                               style={'font-size':'20px'})],\
                                                                               style={'display':'inline-block',\
                                                                                      'width':'100px',\
                                                                                      'vertical-align':'top'}),\
                                                                     html.Div(id='averageStats-teams-dropdown-div',\
                                                                              children=[dcc.Dropdown(id='averageStats-teams-dropdown',\
                                                                                                     options=[],\
                                                                                                     multi = False)],\
                                                                              style={'display':'inline-block',
                                                                                     'width':'200px',\
                                                                                     'vertical-align':'top'})]),\
                                                  html.Div(id='averageStats-display',\
                                                           style={'width':'300px'},\
                                                           children=[html.Div(id='displayLabel',\
                                                                              children=[html.B('Display:',\
                                                                                               style={'font-size':'20px'})],\
                                                                               style={'display':'inline-block',\
                                                                                      'width':'100px',\
                                                                                      'vertical-align':'top'}),\
                                                                     html.Div(id='averageStats-display-dropdown-div',\
                                                                              children=[dcc.Dropdown(id='averageStats-display-dropdown',\
                                                                                                     options=[{'label':'OLS Estimation Table','value':'olsEstTab'},\
                                                                                                              {'label':'Bayesian Estimation Table','value':'bayesEstTab'},\
                                                                                                              {'label':'Bayesian Distribution','value':'bayesDistr'}],\
                                                                                                     multi=False)],\
                                                                              style={'display':'inline-block',
                                                                                     'width':'200px',\
                                                                                     'vertical-align':'top'})]),\
                                                  html.Div(id='averageStats-colNames',\
                                                           style={'visibility':'hidden'},\
                                                           children=[html.Div(id='colNamesLabel',\
                                                                              children=[html.B('Columns:',\
                                                                                               style={'font-size':'20px'})],\
                                                                               style={'display':'inline-block',\
                                                                                      'width':'100px',\
                                                                                      'vertical-align':'top'}),\
                                                                     html.Div(id='averageStats-colNames-dropdown-div',\
                                                                              children=[dcc.Dropdown(id='averageStats-colNames-dropdown',\
                                                                                                     options=[],\
                                                                                                     multi=True)],\
                                                                              style={'display':'inline-block',
                                                                                     'min-width':'200px',\
                                                                                     'vertical-align':'top'})])]),\
                               
                               html.Div(id='tab-content-matchStats',\
                                        style={'visibility':'hidden'},\
                                        children=[html.Div(id='match-StatsLabel',\
                                                           children=[html.B('Columns:',\
                                                                            style={'font-size':'20px'})],\
                                                           style={'display':'inline-block',\
                                                                  'width':'100px',\
                                                                  'vertical-align':'top'}),\
                                                  html.Div(id='matchStats-dropdown-div',\
                                                           children=[dcc.Dropdown(id='matchStats-dropdown',\
                                                                                  options=[],\
                                                                                  multi = True)],\
                                                           style={'display':'inline-block',
                                                                  'min-width':'300px',\
                                                                  'max-width':'900px',\
                                                                  'vertical-align':'top'})]),\
                               
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
                                        children=[html.Div(id='averageStats-output'),\
                                                  html.Div(id='matchStats-table')]),\
                               dcc.Interval(id='interval',\
                                            interval=60*60*1000,\
                                            n_intervals=0)])

######################################################################################
# Variables that will change when connected to backend (currently using Blue Alliance)
api_key = '3BFWLXdBe4yJUCo73Ky3hiBLdKNwCWHe9Nm1Xwr3JSIv5oOM3S1UNdufyTMKBAVU'
headers = {'X-TBA-Auth-Key':api_key}
######################################################################################

# Show years
@app.callback([Output('event-div','style'),\
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

# Display reports
@app.callback(Output('multiselect-reports-label','style'),\
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

# Dictates which report content will be displayed
@app.callback([Output('submit-div','style'),\
               Output('averageStats-teams-dropdown','options'),\
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
                         'line-height':'0px',\
                         'padding-bottom':'0px',\
                         'padding-top':'0px',\
                         'padding-left':'0px'}
    matchStatsStyle = {'visibility':'hidden',\
                       'height':'0px',\
                       'line-height':'0px',\
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
    aveStatsTeams = []
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
        averageStatsStyle = {'visibility':'visible',\
                             'padding-bottom':'10px',\
                             'padding-top':'10px',\
                             'padding-left':'0px'}
        rank_df = parserFuncs.frc_eventRankings(key, api_key)
        teamsList = list(rank_df['team_key'])
        teamsList.sort()

        aveStatsTeams = [{'label':team, 'value':team} for team in teamsList]
    
    elif tab == 'Match Stats':
        # Getting the list of things, FRC match function, with event key: obtain data frame
        # make seperate empty content for html things to include drop down
        matchStatsStyle = {'visibility':'visible',\
                           'padding-bottom':'10px',\
                           'padding-top':'10px',\
                           'padding-left':'0px',\
                           'width':'1000px'}
        match_stats_df = pd.DataFrame()
        
        try:
            match_stats_df = parserFuncs.frc_matchData(key, api_key)
        except:
            matchStatsoptions.append({'label': 'no data available', 'value': ''})
        
        if not (match_stats_df.empty):

            uniqueCols = []
            for col in match_stats_df:
                if not (col in ['blue1','blue2','blue3','red1','red2','red3']):
                    splitCol = col.split('.')

                    if (splitCol[0] == 'blue') | (splitCol[0] == 'red'):
                        uniqueCols.append('color.'+splitCol[1])
                    else:
                        uniqueCols.append(col)
                    
            uniqueCols = list(set(uniqueCols))
            uniqueCols.sort()
            matchStatsoptions = [{'label': val.split('.')[1], 'value': val} if val.split('.')[0] == 'color' else {'label': val, 'value': val} for val in uniqueCols ]

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

    return submitStyle, aveStatsTeams, averageStatsStyle, matchStatsoptions, matchStatsStyle, contentDraftSim, draftSimulatorStyle, contentRankModel, rankModelStyle, contentEliminationSim, eliminationSimulatorStyle

# Callback for match statistics report
@app.callback([Output('matchStats-table','children'),\
               Output('matchStats-table','style')],\
              [Input('submit','n_clicks'),
               Input('tabs-reports','value')],\
              [State('matchStats-dropdown','value'),\
               State('event-dropdown','value')])
def update_matchStats_table(n_clicks,\
                            tabVal,\
                            multi_choices,\
                            eventKey):
    
    if (tabVal == 'Match Stats'):
        outputStyle = {'visibility':'visible'}

        if multi_choices:
            df = parserFuncs.frc_matchData(eventKey, api_key)

            blueAlliList = ['blue.'+value.split('.')[1] for value in multi_choices if value.split('.')[0] == 'color']
            redAlliList = ['red.'+value.split('.')[1] for value in multi_choices if value.split('.')[0] == 'color']
            nonAlliList = [value for value in multi_choices if value.split('.')[0] != 'color']

            col_list = ['blue1','blue2','blue3','red1','red2','red3'] + nonAlliList + blueAlliList + redAlliList
            #updated_table = generate_table(df.loc[:,col_list],'matchStats','Match Stats')

            subsetDF = df.loc[:,col_list]
            #col_list = [x.replace('.','_') for x in col_list]

            title = html.Div(id='matchStats-title-div',\
                             children=html.B('Match Stats',\
                                             style={'font-size':'40px'}))
            
            temp = html.Div(id='matchStats-table-div',\
                            children=[dash_table.DataTable(id='matchStats-table-output',\
                                                           columns=[{'name': i, 'id': i} for i in col_list],\
                                                           style_cell={'textAlign':'left'},\
                                                           data=subsetDF.to_dict('records'),\
                                                           filter_action='native',\
                                                           sort_action='native',\
                                                           sort_mode='multi')])
            
            tempData = subsetDF.copy()
            csv_string = tempData.to_csv(index=False, encoding='utf-8')
            csv_string = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(csv_string)

            downloadDiv = html.A('Download Table',\
                                 id='matchStat-download-button',\
                                 download='matchStats.csv',\
                                 href=csv_string,\
                                 style={'font-size':'20px'})

            output = [title,downloadDiv,temp]

        else:
            error_output = generate_error_div('matchStats',\
                                              'Please select a column value')
            output = [error_output]

    else:
        output = []
        outputStyle = {'visibility':'hidden'}
        
    return output, outputStyle

# Callback for showing and populating column dropdown for average team statistics report
@app.callback([Output('averageStats-colNames','style'),\
               Output('averageStats-colNames-dropdown','options')],\
              [Input('averageStats-display-dropdown','value')],\
              [State('event-dropdown','value')])
def display_colDropdown(displayType,\
                        eventKey):
    colStyle = {'visibility':'hidden'}
    colOptions = []

    if not(displayType is None):
        if (displayType == 'bayesEstTab') | (displayType == 'bayesDistr'):
            colStyle = {'visibility':'visible',\
                        'min-width':'300px'}
            
            match_stats_df = pd.DataFrame()
            
            try:
                match_stats_df = parserFuncs.frc_matchData(eventKey, api_key)
            except:
                colOptions.append({'label': 'no data available', 'value': ''})
            
            if not (match_stats_df.empty):

                uniqueCols = []
                for col in match_stats_df:
                    if not (col in ['blue1','blue2','blue3','red1','red2','red3','matchKey']):
                        splitCol = col.split('.')

                        if (splitCol[0] == 'blue') | (splitCol[0] == 'red'):
                            uniqueCols.append('color.'+splitCol[1])
                        else:
                            uniqueCols.append(col)
                        
                uniqueCols = list(set(uniqueCols))
                uniqueCols.sort()
                colOptions = [{'label': val.split('.')[1], 'value': val} if val.split('.')[0] == 'color' else {'label': val, 'value': val} for val in uniqueCols ]
    
    return colStyle,colOptions

# Callback for average team statistics report
@app.callback([Output('averageStats-output','children'),\
               Output('averageStats-output','style')],\
              [Input('submit','n_clicks'),
               Input('tabs-reports','value')],\
              [State('averageStats-teams-dropdown','value'),\
               State('averageStats-display-dropdown','value'),\
               State('averageStats-colNames-dropdown','value'),\
               State('event-dropdown','value')])
def update_averageTeamStats(n_clicks,\
                            tabVal,\
                            teamValue,\
                            displayType,\
                            colValues,\
                            eventKey):
    
    if (tabVal == 'Average Stats by Team'):
        outputStyle = {'visibility':'visible',\
                       'padding-bottom':'10px',\
                       'padding-top':'10px',\
                       'padding-left':'0px'}

        if teamValue and displayType:
            match_df = parserFuncs.frc_matchData(eventKey, api_key)
            rank_df = parserFuncs.frc_eventRankings(eventKey, api_key)

            matchDataDF = match_df.drop(columns=['matchKey'])
            rankTable = rank_df.loc[:,['rank','team_key']]
            rankTable = rankTable.rename(columns={'team_key':0})

            # Get X matrix
            xData = teamStatFuncs.create_xMatrix(matchDataDF,\
                                                 rankTable)
            
            # Get Y matrix
            output = teamStatFuncs.create_yMatrix(matchDataDF,\
                                                  rankTable)
            y_OffData = output[0]
            y_DefData = output[1]
            colNames = output[2]
            robotSpecCols = output[3]
            #nonAlliSpecCols = output[4]

            # Prepare to add output table/charts
            tempOutput = []

            if displayType == 'olsEstTab':
                # Get average data for OLS
                beta_Off_DF,beta_Def_DF = teamStatFuncs.OLS_TeamStats(xData,\
                                                                      y_OffData,\
                                                                      y_DefData,\
                                                                      colNames,\
                                                                      rankTable)
                beta_Off_DF.columns = ['Off_'+x for x in beta_Off_DF.columns]
                beta_Def_DF.columns = ['Def_'+x for x in beta_Def_DF.columns]

                roboSpecStats = teamStatFuncs.specTeamStats(robotSpecCols,\
                                                            matchDataDF,\
                                                            rankTable)

                # Create seperate concatenated dataframe
                concatDF = pd.concat([roboSpecStats,beta_Off_DF,beta_Def_DF],\
                                     axis=1,\
                                     sort=False)

                # Filter for specific team
                beta_Off_DF = beta_Off_DF.loc[teamValue,:]
                beta_Def_DF = beta_Def_DF.loc[teamValue,:]
                roboSpecStats = roboSpecStats.loc[teamValue,:]

                # Transpose dataframe
                beta_Off_DF = beta_Off_DF.T
                beta_Def_DF = beta_Def_DF.T
                roboSpecStats = roboSpecStats.T

                # Add row names a column and rename them their feature name appropriately
                beta_Off_DF = beta_Off_DF.reset_index(drop=False, inplace=False)
                beta_Def_DF = beta_Def_DF.reset_index(drop=False, inplace=False)
                roboSpecStats = roboSpecStats.reset_index(drop=False, inplace=False)

                beta_Off_DF = beta_Off_DF.rename(columns={0:'Offensive Stats'})
                beta_Def_DF = beta_Def_DF.rename(columns={0:'Defensive Stats'})
                roboSpecStats = roboSpecStats.rename(columns={0:'Robot Specific'})

                # Output creation
                #--------------------------------------------------------------------------------------------------------------
                # Titles and subtitles
                title = html.Div(id='olsEstTab-title-div',\
                                 children=html.B('OLS Estimation Stats',\
                                                 style={'font-size':'40px'}))

                roboTitle = html.Div(id='roboSpec-title-div',\
                                     children=html.B('Robot Specific',\
                                                     style={'font-size':'20px'}))
                offTitle = html.Div(id='beta_off-title-div',\
                                    children=html.B('Offensive Stats',\
                                                    style={'font-size':'20px'}))
                defTitle = html.Div(id='beta_def-title-div',\
                                    children=html.B('Defensive Stats',\
                                                    style={'font-size':'20px'}))

                # Div for tables
                temp = html.Div(id='olsEstTab-tables-div',\
                                children=[html.Div(id='roboSpec-table-div',\
                                                   style={'display':'inline-block',\
                                                          'padding-left':'20px'},\
                                                   children=[roboTitle,\
                                                             dash_table.DataTable(id='roboSpec-table',\
                                                                                  columns=[{'name': i, 'id': i} for i in roboSpecStats.columns],\
                                                                                  style_cell={'textAlign':'left'},\
                                                                                  data=roboSpecStats.to_dict('records'),\
                                                                                  filter_action='native',\
                                                                                  sort_action='native',\
                                                                                  sort_mode='multi')]),\
                                          html.Div(id='beta_off-table-div',\
                                                   style={'display':'inline-block',\
                                                          'padding-left':'20px'},\
                                                   children=[offTitle,\
                                                             dash_table.DataTable(id='beta_off-table',\
                                                                                  columns=[{'name': i, 'id': i} for i in beta_Off_DF.columns],\
                                                                                  style_cell={'textAlign':'left'},\
                                                                                  data=beta_Off_DF.to_dict('records'),\
                                                                                  filter_action='native',\
                                                                                  sort_action='native',\
                                                                                  sort_mode='multi')]),\
                                          html.Div(id='beta_def-table-div',\
                                                   style={'display':'inline-block',\
                                                          'padding-left':'20px'},\
                                                   children=[defTitle,\
                                                             dash_table.DataTable(id='beta_def-table',\
                                                                                  columns=[{'name': i, 'id': i} for i in beta_Def_DF.columns],\
                                                                                  style_cell={'textAlign':'left'},\
                                                                                  data=beta_Def_DF.to_dict('records'),\
                                                                                  filter_action='native',\
                                                                                  sort_action='native',\
                                                                                  sort_mode='multi')])])

                # Download link (all teams)
                tempData = concatDF.copy()
                csv_string = tempData.to_csv(index=False, encoding='utf-8')
                csv_string = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(csv_string)

                downloadDiv = html.A('Download Table (All Teams)',\
                                     id='olsEstTab-download-button',\
                                     download='allTeams_olsStats.csv',\
                                     href=csv_string,\
                                     style={'font-size':'20px',\
                                            'visibility':'visible'})
                
                tempOutput.append(title)
                tempOutput.append(downloadDiv)
                tempOutput.append(temp)

            elif (displayType == 'bayesEstTab') | (displayType == 'bayesDistr'):
                if colValues:
                    if len(colValues) <= 500/len(rank_df):
                        # Perform MCMC simulation
                        alliList = [value.split('.')[1] for value in colValues if value.split('.')[0] == 'color']
                        
                        y_colIndices = [colNames.index(x) for x in colNames if x in alliList]

                        concatArray = np.concatenate((y_OffData[:,y_colIndices],y_DefData[:,y_colIndices]),\
                                                     axis=1)

                        offColList = ['off_'+x for x in alliList]
                        defColList = ['def_'+x for x in alliList]
                        conColList = offColList+defColList

                        results,betaDict = teamStatFuncs.bayes_TeamStat(xData,\
                                                                        concatArray,\
                                                                        conColList,\
                                                                        rankTable,\
                                                                        nIter=5000,\
                                                                        nChains=4,\
                                                                        nJobs=4)
                        
                        results = results.rename(columns=betaDict)

                        if displayType == 'bayesEstTab':
                            results.columns = ['_'.join(x) if ((type(x) == tuple) & (teamValue in x)) else x for x in results.columns]
                            subsetResults = results.loc[:,[x for x in results.columns if type(x) == str]]

                            title = html.Div(id='bayesEstTab-title-div',\
                                             children=html.B('Bayesian Estimation Stats',\
                                                             style={'font-size':'40px'}))
                        
                            temp = html.Div(id='bayesEstTab-table-div',\
                                            children=[dash_table.DataTable(id='bayesEstTab-table',\
                                                                        columns=[{'name': i, 'id': i} for i in subsetResults.columns],\
                                                                        style_cell={'textAlign':'left'},\
                                                                        data=subsetResults.to_dict('records'),\
                                                                        filter_action='native',\
                                                                        sort_action='native',\
                                                                        sort_mode='multi')])

                            tempData = results.copy()
                            csv_string = tempData.to_csv(index=False, encoding='utf-8')
                            csv_string = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(csv_string)

                            downloadDiv = html.A('Download Table',\
                                                id='bayesEsti-download-button',\
                                                download='bayesResults.csv',\
                                                href=csv_string,\
                                                style={'font-size':'20px',\
                                                        'visibility':'visible'})
                            
                            tempOutput.append(title)
                            tempOutput.append(downloadDiv)
                            tempOutput.append(temp)

                        elif displayType == 'bayesDistr':
                            title = html.Div(id='bayesDistr-title-div',\
                                             children=html.B('Bayes Distribution(s)',\
                                                             style={'font-size':'40px'}))

                            graphList = []
                            for colVal in conColList:
                                fig, gauss_kde = teamPlotFuncs.plot_trace(results[(colVal,teamValue)],\
                                                                          param_name=colVal+' '+teamValue)
                                graphList.append(dcc.Graph(id=colVal+'-div',\
                                                           figure=fig,\
                                                           style={'width':'1500px',\
                                                                  'height':'750px'}))
                            
                            temp = html.Div(id='bayesDistr-chart-div',\
                                            children=graphList)
                            
                            tempOutput.append(title)
                            tempOutput.append(temp)

                    else:
                        from math import floor
                        error_output = generate_error_div('aveStats',\
                                                          'Please select only '+str(floor(1000/len(rank_df)))+' or fewer columns')
                        tempOutput = [error_output]
            
            output = tempOutput
        else:
            error_output = generate_error_div('aveStats',\
                                              'Please select either a team or a display type')
            
            output = [error_output]

    else:
        output = []
        outputStyle = {'visibility':'hidden',\
                       'height':'0px',\
                       'padding-bottom':'0px',\
                       'padding-top':'0px',\
                       'padding-left':'0px'}
        
    return output, outputStyle


# General Functions (NOT callbacks)
#############################################################################################

# Generate error message
def generate_error_div(divID,title):
    error_div = html.Div(id=divID+'-div',\
                         style={'padding-bottom':'10px',\
                                'padding-top':'10px',\
                                'padding-left':'0px'},\
                         children=[html.B(title,\
                                          style={'font-size':'20px',\
                                                 'color':'red'})])
    
    return error_div

if __name__ == '__main__':
    app.run_server(debug=True)