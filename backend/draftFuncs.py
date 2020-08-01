from random import random

def frc_draftFunc(teamData,numOfAllis=8,numOfTeams=3):
    '''
    Variables for frc_draftFunc
    ---------------------------------------
    keyword         type        explanation
    ------------    -------     -----------
    teamData        list        list of dictionaries of team data for creating alliances.  See list of variables below
    numOfAllis      int         number of alliances
    numOfTeams      int         numbers of teams in each alliance

    output          type        explanation
    ------          -------     -----------
    allianceList    list        list of dictionaries of alliance data
        
    Variables for each team in teamData:
    --------------------------------------------------------------------------------
    team          = team number
    rank          = rank based on qualification results
    score         = value that determines team ultility (i.e., OPR, DPR, CCWM, etc.)
    probAccept    = probability of team accepting alliance offer
    decline       = whether team declined offer to join an alliance
    --------------------------------------------------------------------------------

    Variables for alliances in allianceList
    --------------------------------------------------------------------------------
    captain       = team that is the captain of alliance, chooses teams
    team1         = the first team chosen by the captain
    team2         = the second team chosen by the captain
    --------------------------------------------------------------------------------
    '''

    # Create alliances based on snake order drafting
    #---------------------------------------------------------------------------
    allianceList = []

    for step in range(2*numOfAllis):
        # Get the current top rank that has not been assigned to an alliance yet.
        topRank = min([item['rank'] for item in teamData])

        if step < numOfAllis:
            # Sets the current alliance
            currAlli = step+1

            # Gets the team entry for the captain team and removes the captain team from the teamData
            captEntry = next((item for item in teamData if item['rank'] == topRank), None)
            teamData = [item for item in teamData if item['team'] != captEntry['team']]
        else:
            # Sets the current alliance
            currAlli = numOfAllis-(step%numOfAllis)

        # Gets the current max score
        maxScore = max([item['score'] for item in teamData])

        declineBool = True
        while declineBool:
            # Gets the team entry for the highest score team and removes that team from the teamData
            teamEntry = next((item for item in teamData if item['score'] == maxScore), None)

            if teamEntry['decline'] == True:
                declineBool = False
            elif teamEntry['probAccept'] >= random():
                declineBool = False
            else:
                declineBool = True
                teamEntry['decline'] = declineBool

                teamIndex = next((i for i, item in enumerate(teamData) if item['team'] == teamEntry['team']), None)
                teamData[teamIndex] = teamEntry
            
            # Gets the current max score
            maxScore = max([item['score'] for item in teamData if item['decline'] == False])

        teamData = [item for item in teamData if item['team'] != teamEntry['team']]

        if step < numOfAllis:
            # Adds these teams to the current alliance
            allianceList.append({'allianceNum':currAlli,'captain':captEntry,'team1':teamEntry})
        else:
            # Finds the current alliance entry and adds the highest scoring team to the current alliance
            alliEntry = next((item for item in allianceList if item['allianceNum'] == currAlli), None)
            alliEntry['team2'] = teamEntry

            # Adds current alliance 
            alliIndex = next((i for i, item in enumerate(allianceList) if item['allianceNum'] == currAlli), None)
            allianceList[alliIndex] = alliEntry
    
    return allianceList