import pandas as pd
import datetime
import numpy as np
from scipy import linalg

import statsmodels.formula.api as smf
import statsmodels.api as sm
import pystan

def bayes_TeamStat(xData,\
                   yData,\
                   yColNames,\
                   teamsTable,\
                   nIter=5000,\
                   nChains=3,\
                   nJobs=3,\
                   beta_mu=0,\
                   beta_sigma=100,\
                   L_Omega_eta=16,\
                   L_sigma_mu=0,\
                   L_sigma_sigma=20):
    '''
    Variables for OLS_TeamStats
    ---------------------------------------
    keyword         type        explanation
    ------------    ---------   -----------
    xData           ndarray     a 2D ndarray that contains the X matrix generated from create_xMatrix()
    yData           ndarray     a 2D ndarray that contains Y matrix
    yColNames       list        list of names of the y columns
    teamsTable      DataFrame   dataframe of the teams and rankings
    nIter           integer     number of iterations for the Stan model (see PyStan documentation, default=5000)
    nChains         integer     number of chains for the Stan model (see PyStan documentation, default=3)
    nJobs           integer     number of jobs for the Stan model (see PyStan documentation, default=3)
    beta_mu         integer     prior mean value for the beta coefficients, normally distributed (default=0)
    beta_sigma      integer     prior standard deviation for the beta coefficients, normally distributed (default=100)
    L_Omega_eta     integer     prior eta for the L Omega lower triangle matrix, lkj correlation Cholesky (default=16)
    L_sigma_mu      integer     prior mean value for the diagonal L sigma matrix, cauchy distribution (default=0)
    L_sigma_sigma   integer     prior standard deviation value for the diagonal L sigma matrix, cauchy distribution (default=20)

    output         type         explanation
    -----------    ---------    -----------
    fit_DF         DataFrame    dataframe of the samples used for all the coefficients
    '''


    if xData.shape[0] == yData.shape[0]:
        stan_code = '''
                    data {
                        int<lower=1> K;
                        int<lower=1> J;
                        int<lower=0> N;
                        vector[J] x[N];
                        vector[K] y[N];
                    }
                    parameters {
                        matrix[K, J] beta;
                        cholesky_factor_corr[K] L_Omega;
                        vector<lower=0>[K] L_sigma;
                    }
                    model {
                        vector[K] mu[N];
                        matrix[K, K] L_Sigma;

                        for (n in 1:N)
                            mu[n] = beta * x[n];

                        L_Sigma = diag_pre_multiply(L_sigma, L_Omega);

                        to_vector(beta) ~ normal('''+str(beta_mu)+''', '''+str(beta_sigma)+''');
                        L_Omega ~ lkj_corr_cholesky('''+str(L_Omega_eta)+''');
                        L_sigma ~ cauchy('''+str(L_sigma_mu)+''', '''+str(L_sigma_sigma)+''');

                        y ~ multi_normal_cholesky(mu, L_Sigma);
                    }
                    '''
        
        data_dict = {'x':xData,\
                     'y':yData,\
                     'J':xData.shape[1],\
                     'N':xData.shape[0],\
                     'K':yData.shape[1]}
        
        stan_model = pystan.StanModel(model_code=stan_code)
        fit_sample = stan_model.sampling(data=data_dict,\
                                         iter=nIter,\
                                         chains=nChains,
                                         n_jobs=nJobs)
        
        fit_DF = fit_sample.to_dataframe()

        # Rename beta columns with corresponding y column names and team numbers
        beta_shape = fit_sample.extract()['beta'].shape

        if (beta_shape[1] == len(yColNames)) & (beta_shape[2] == len(teamsTable)):
            betaDict = {}
            
            for i in range(beta_shape[1]):
                for j in range(beta_shape[2]):
                    col1 = yColNames[i]
                    col2 = teamsTable.at[j,0]

                    betaDict['beta['+str(i+1)+','+str(j+1)+']'] = (col1,col2)
            
            #fit_DF = fit_DF.rename(columns=betaDict)
        else:
            return 'Number of beta sampling columns ('+str(beta_shape[1])+') != colNames ('+str(len(yColNames))+') and/or rows ('+str(beta_shape[2])+') != number of teams ('+str(len(teamsTable))+')'
    else:
        return 'X matrix and Y matrix do not have the same number of rows'

    return fit_DF,betaDict

def OLS_TeamStats(xData,y_OffData,y_DefData,colNames,teamsTable):
    '''
    Variables for OLS_TeamStats
    ---------------------------------------
    keyword         type        explanation
    ------------    ---------   -----------
    xData           ndarray     a 2D ndarray that contains the X matrix generated from create_xMatrix()
    y_OffData       ndarray     a 2D ndarray that contains the Y offensive matrix generated from create_yMatrix
    y_DefData       ndarray     a 2D ndarray that contains the Y defensive matrix generated from create_yMatrix
    colNames        list        list of column names for the both the Y offensive and defensive matrices
    teamsTable      DataFrame   dataframe of team names and rankings

    output         type            explanation
    -----------    ---------       -----------
    beta_Off_DF    DataFrame       dataframe of the calculated beta coefficients for offensive stats
    beta_Def_DF    DataFrame       dataframe of the calculated beta coefficients for defensive stats
    '''
    # Calculating beta coefficients for offensive and defensive stats
    #-------------------------------------------------------------------------------
    # Confirming that the number of rows match for xData and y_OffData.
    if xData.shape[0] == y_OffData.shape[0]:
        beta_Off = linalg.inv(xData.T.dot(xData)).dot(xData.T).dot(y_OffData)
        beta_Off_DF = pd.DataFrame(beta_Off,\
                                   index=teamsTable[0],\
                                   columns=colNames)
    else:
        beta_Off_DF = None
    
    # Confirming that the number of rows match for xData and y_DefData.
    if xData.shape[0] == y_DefData.shape[0]:
        beta_Def = linalg.inv(xData.T.dot(xData)).dot(xData.T).dot(y_DefData)
        beta_Def_DF = pd.DataFrame(beta_Def,\
                                   index=teamsTable[0],\
                                   columns=colNames)
    else:
        beta_Def_DF = None
    
    return beta_Off_DF,beta_Def_DF

def specTeamStats(robotSpecCols,teamMatchDF,teamsTable):
    '''
    Variables for specTeamStats
    ---------------------------------------
    keyword          type         explanation
    -------------    ---------    -----------
    robotSpecCols    list         list of robot specific columns
    teamMatchDF      DataFrame    dataframe of the match data for a given event
    teamsTable       DataFrame    dataframe of team names and rankings

    output           type         explanation
    -------------    ---------    -----------
    roboSpecStats    DataFrame    dataframe of the specific robotics statistics
    '''
    #Adding the robot specific attributes to each robot
    #-------------------------------------------------------------------------------
    # Make an empty dataframe to add robot specific data
    roboSpecStats = pd.DataFrame(index=teamsTable[0],\
                                 columns=[0])
    
    for specCol in robotSpecCols:
        # Getting the robot column name and general column name that corresponds to that attribute
        # (i.e., blue1 and autoRobot form blue.autoRobot1).
        stringColSplit = specCol.split('.')
        alliColor = stringColSplit[0]

        robotColName = alliColor+stringColSplit[-1][-1]
        genRobotAttr = stringColSplit[-1][:-1]

        # Get the unique value from each robot specific column
        uniqueAttriList = teamMatchDF[specCol].unique()

        for uniqueAttriVal in uniqueAttriList:
            # Returning the unique colun names that result from the unique attribute
            newColName = genRobotAttr+'.'+uniqueAttriVal

            # For the first instance, add a new column to roboSpecStats.
            # If the column already exits in roboSpecStats, continue.
            # Else, add column to roboSpecStats.
            if 0 in roboSpecStats.columns.values:
                roboSpecStats.rename(columns={0:newColName},inplace=True)
                roboSpecStats[newColName] = 0
            elif not (newColName in roboSpecStats.columns.values):
                roboSpecStats[newColName] = 0
            
            for team in teamsTable[0]:
                rowsTeams = teamMatchDF.loc[teamMatchDF[robotColName] == team,robotColName]

                # Sum the instances in which that team performed that task and add it to the previous value in robotSpecCols
                # (i.e., autoRobot.None = did not perform autonomous).
                # This is accomplished by exploiting the fact that "True" returns 1.
                value = (teamMatchDF.loc[rowsTeams.index,specCol] == uniqueAttriVal).sum()
                roboSpecStats.at[team,newColName] += value

    return roboSpecStats

def create_xMatrix(teamMatchDF,teamsTable):
    '''
    Variables for create_xMatrix
    ---------------------------------------
    keyword          type         explanation
    -------------    ---------    -----------
    teamMatchDF      DataFrame    dataframe of the match data for a given event
    teamsTable       DataFrame    dataframe of team names and rankings

    output           type         explanation
    -------------    ---------    -----------
    X                ndarray      array of the X matrix
    '''
    # Setting up the X matrix
    nRows = 2*teamMatchDF.shape[0]
    nCols = len(teamsTable)

    X = np.zeros((nRows,nCols))

    for xRowInd in range(nRows):
        if xRowInd%2 == 0:
            colShift = 0
            rowShift = int(xRowInd/2)
        elif xRowInd%2 == 1:
            colShift = 3
            rowShift = int((xRowInd-1)/2)
        
        for colNum in range(0+colShift,3+colShift):
            colName = teamMatchDF.columns.values[colNum]
            xColInd = teamsTable.index[teamsTable[0] == teamMatchDF.at[rowShift,colName]].tolist()[0]

            X[xRowInd,xColInd] = 1

    return X

def create_yMatrix(teamMatchDF,teamsTable):
    '''
    Variables for create_yMatrix
    ---------------------------------------
    keyword          type         explanation
    -------------    ---------    -----------
    teamMatchDF      DataFrame    dataframe of the match data for a given event
    teamsTable       DataFrame    dataframe of team names and rankings

    output           type         explanation
    -------------    ---------    -----------
    Y_off            ndarray      array of the Y matrix for offensive match data
    Y_def            ndarray      array of the Y matrix for offensive match data
    colNames         list         list of column names for the both the Y offensive and defensive matrices
    robotSpecsCols   list         list of robot specific columns
    nonAlliSpecsCols list         list of non-alliance specific columns
    '''
    # Before setting up the Y matrix, data types need to be converted to numeric values
    # Specifically, boolean columns need to be converted to int64 and object columns to category

    # Create array of robot specific stats (i.e., blue.autoRobot1)
    robotSpecsCols = [s for s in teamMatchDF.columns.values if 'Robot' in s]

    # Create array of non-alliance specific stats (i.e., coopertition)
    nonAlliSpecsCols = [s for s in teamMatchDF.columns.values if (not s.startswith('blue'))&(not s.startswith('red'))]

    for i in range(6,len(teamMatchDF.columns.values)):
        colName = teamMatchDF.columns.values[i]

        if teamMatchDF[colName].dtype == 'bool':
            teamMatchDF[colName] = teamMatchDF[colName].astype('int64')
        elif teamMatchDF[colName].dtype == 'object':
            teamMatchDF[colName] = teamMatchDF[colName].astype('category')

    # Creating a numeric dataframe with only a subset of the data (exclude team numbers, just match data).
    # Also, removing robot specific stats (these stats would not be helpful for the Y matrix)
    numMatchData = teamMatchDF.copy()
    numMatchData = numMatchData.drop(robotSpecsCols, axis=1)
    numMatchData = numMatchData.drop(nonAlliSpecsCols, axis=1)
    numMatchData = pd.get_dummies(numMatchData.iloc[:,6:len(numMatchData.columns.values)])
    numMatchData = numMatchData[np.sort(numMatchData.columns.tolist())]

    # Setting up the Y matrix for the teams
    yRows = 2*numMatchData.shape[0]
    colNames = []

    # Find the center column index between blue and red alliance columns
    nCols = len(numMatchData.columns.values)

    if nCols%2 == 0:
        yCols = int(nCols/2)

        # Data in terms of offense perspective (i.e., Offensive Power Rankings (OPR))
        Y_off = np.zeros((yRows,yCols))

        # Data in terms of defensive perspective (i.e., Defensive Power Rankings (DPR))
        Y_def = np.zeros((yRows,yCols))

        for yRowInd in range(yRows):
            if yRowInd%2 == 0:
                colShift = 0
                rowShift = int(yRowInd/2)
            elif yRowInd%2 == 1:
                colShift = yCols
                rowShift = int((yRowInd-1)/2)
            
            for dfColNum in range(yCols):
                colNameOff = numMatchData.columns.values[dfColNum+colShift]
                colNameDef = numMatchData.columns.values[dfColNum+(yCols-colShift)]

                Y_off[yRowInd,int(dfColNum-colShift)] = numMatchData.at[rowShift,colNameOff]
                Y_def[yRowInd,int(dfColNum-colShift)] = numMatchData.at[rowShift,colNameDef]

                if (colNameOff.split('.')[-1] == colNameDef.split('.')[-1])&(yRowInd == 0):
                    colNames.append(colNameOff.split('.')[-1])
    else:
        return 'Error: Number of blue columns is not equal to red columns'
    
    return Y_off,Y_def,colNames,robotSpecsCols,nonAlliSpecsCols
