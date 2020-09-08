import requests
import pandas as pd

def frc_matchData(eventKey, secretKey='omq7mnigcke5e7k1e1udlitgo8h0kke2'):
    token = requests.get('https://frc-event-statistics.i.tgcloud.io:9000/requesttoken?secret='+secretKey+'&lifetime=1000000')
    tokenJSON = token.json()

    header = {'Authorization': 'Bearer '+tokenJSON['token']}
    url = 'https://frc-event-statistics.i.tgcloud.io:9000/graph/MyGraph/vertices/EventMatches?filter=event_key="'+eventKey+'"'

    page = requests.get(url,\
                        headers=header)
    
    matchData = pd.DataFrame(page.json()['results'])

    for row in range(len(matchData)):
        currRow = matchData.at[row,'attributes']

        for col in list(currRow.keys()):
            matchData.at[row,col] = currRow[col]
    
    matchData = matchData.rename(columns={'v_id':'matchKey'})

    return matchData

def frc_eventRankings(eventKey, secretKey='omq7mnigcke5e7k1e1udlitgo8h0kke2'):
    token = requests.get('https://frc-event-statistics.i.tgcloud.io:9000/requesttoken?secret='+secretKey+'&lifetime=1000000')
    tokenJSON = token.json()

    header = {'Authorization': 'Bearer '+tokenJSON['token']}
    url = 'https://frc-event-statistics.i.tgcloud.io:9000/graph/MyGraph/vertices/EventRankings?filter=event_key="'+eventKey+'"'

    page = requests.get(url,\
                        headers=header)
    
    rankData = pd.DataFrame(page.json()['results'])

    for row in range(len(rankData)):
        currRow = rankData.at[row,'attributes']

        rankData.at[row,'team_key'] = currRow['fr_team']

    rankData = rankData.rename(columns={'v_id':'rank'})
    rankData['rank'] = rankData['rank'].apply(lambda x: x.split('_')[2])
    rankData = rankData.loc[:,['rank','team_key']]

    return rankData
