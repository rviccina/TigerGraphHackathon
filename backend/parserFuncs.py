import requests
import pandas as pd
#from pandas.io.json import json_normalize
from pandas import json_normalize


def frc_matchData(eventKey, TBA_auth_key, qualBool=True):
    '''
    Variables for frc_matchData
    ---------------------------------------
    keyword         type        explanation
    ------------    -------     -----------
    eventKey        string      unique string that indicates which year and event to pull match data from (ex: 2018azfl)
    TBA_auth_key    string      unique string that authenticates user for accessing Blue Alliance data
    qualBool        boolean     boolean to determine whether qualification or elimination match data is provided (default: True)

    output    type            explanation
    ------    ---------       -----------
    df        DataFrame       pandas dataframe that contains all of the match data
    '''
    # Set up TBA headers
    headers = {'X-TBA-Auth-Key': TBA_auth_key}

    # Pull match data for specific event
    matchesURL = 'https://www.thebluealliance.com/api/v3/event/'+eventKey+'/matches'
    page = requests.get(matchesURL,
                        headers=headers)

    matchesTable = pd.DataFrame(page.json())
    ################################################################################################

    # Extract qualification data from event
    if qualBool:
        qualsTable = matchesTable.loc[matchesTable['comp_level'] == 'qm', :]

        alliances = qualsTable['alliances'].reset_index(drop=True)
        matchKeys = qualsTable['key'].reset_index(drop=True)
        scoreBreakdown = qualsTable['score_breakdown'].reset_index(drop=True)

        noneCheckBool = all([x is None for x in scoreBreakdown])
    
        if noneCheckBool:
            scoreBreakdown = alliances.copy()

        nScoreBreakdown = len(scoreBreakdown)
    else:
        elimTable = matchesTable.loc[matchesTable['comp_level'] != 'qm', :]

        alliances = elimTable['alliances'].reset_index(drop=True)
        matchKeys = elimTable['key'].reset_index(drop=True)
        scoreBreakdown = elimTable['score_breakdown'].reset_index(drop=True)

        noneCheckBool = all([x is None for x in scoreBreakdown])
    
        if noneCheckBool:
            scoreBreakdown = alliances.copy()

        nScoreBreakdown = len(scoreBreakdown)

    for j in range(nScoreBreakdown):
        # Splits and consolidates teams from blue alliance (blueAlli) and red alliance (redAlli)
        alliTeams = pd.DataFrame.from_dict(json_normalize(alliances[j]), orient='columns')
        blueAlli = pd.DataFrame([alliTeams['blue.team_keys'][0]], columns=['blue1', 'blue2', 'blue3'])
        redAlli = pd.DataFrame([alliTeams['red.team_keys'][0]], columns=['red1', 'red2', 'red3'])

        if j == 0:
            df = pd.DataFrame.from_dict(json_normalize(scoreBreakdown[j]),
                                        orient='columns')

            if noneCheckBool:
                df = df.loc[:, ['blue.score', 'red.score']]

            df = pd.concat([blueAlli, redAlli, df],
                           axis=1,
                           sort=False)

            df.at[j, 'matchKey'] = matchKeys[j]
        else:
            temp = pd.DataFrame.from_dict(json_normalize(scoreBreakdown[j]),
                                          orient='columns')
            if noneCheckBool:
                temp = temp.loc[:, ['blue.score', 'red.score']]

            temp = pd.concat([blueAlli, redAlli, temp],
                             axis=1,
                             sort=False)
            df = df.append(temp,
                           sort=False)
            df = df.reset_index(drop=True)

            df.at[j, 'matchKey'] = matchKeys[j]
            
    return df


def frc_eventRankings(eventKey,TBA_auth_key):
    '''
    Variables for frc_eventRankings
    ---------------------------------------
    keyword         type        explanation
    ------------    -------     -----------
    eventKey        string      unique string that indicates which year and event to pull match data from (ex: 2018azfl)
    TBA_auth_key    string      unique string that authenticates user for accessing Blue Alliance data

    output    type            explanation
    ------    ---------       -----------
    df        DataFrame       pandas dataframe that contains all of the rank data
    '''
    # Set up TBA headers
    headers = {'X-TBA-Auth-Key': TBA_auth_key}

    # Pull ranking data for specific event
    teamsURL = 'https://www.thebluealliance.com/api/v3/event/'+eventKey+'/rankings'
    page = requests.get(teamsURL,
                        headers=headers)
    data = page.json()
    rankingTable = pd.DataFrame(data['rankings'])
    ################################################################################################

    return rankingTable
