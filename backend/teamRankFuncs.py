import pandas as pd

import statsmodels.formula.api as smf
import statsmodels.api as sm
import pystan

from scipy.stats import shapiro, normaltest, anderson
from scipy.stats import ttest_1samp, wilcoxon

def bayes_TeamRankModel(teamData,\
                        rankData,\
                        nIter=5000,\
                        nChains=3,\
                        nJobs=3,\
                        priorType='uniformBeta',\
                        stanDictVar={'alpha_mu':0,\
                                     'alpha_sigma':2}):
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


    if teamData.shape[0] == rankData.shape[0]:
        
        if priorType == 'Laplace':
            beta_mu = stanDictVar['beta_mu']#0
            beta_sigma = stanDictVar['beta_sigma']#10

            alpha_mu = stanDictVar['alpha_mu']#0
            alpha_sigma = stanDictVar['alpha_sigma']#2

            stan_code = '''
                        data {
                            int<lower=2> K;
                            int<lower=0> N;
                            int<lower=1> D;
                            int<lower=1,upper=K> y[N];
                            row_vector[D] x[N];
                        }
                        parameters {
                            vector[D] beta;
                            ordered[K-1] c;
                            real alpha;
                        }
                        model {
                            // Strongly regularizing priors
                            beta ~ double_exponential('''+str(beta_mu)+''', '''+str(beta_sigma)+''');

                            alpha ~ normal('''+str(alpha_mu)+''', '''+str(alpha_sigma)+''');

                            for (n in 1:N)
                                y[n] ~ ordered_logistic(x[n] * beta + alpha, c);
                        }
                        '''
        elif priorType == 'horseshoe':
            beta_tilde_mu = stanDictVar['beta_tilde_mu']#0
            beta_tilde_sigma = stanDictVar['beta_tilde_sigma']#1

            lambda_mu = stanDictVar['lambda_mu']#0
            lambda_sigma = stanDictVar['lambda_sigma']#1

            tau_tilde_mu = stanDictVar['tau_tilde_mu']#0
            tau_tilde_sigma = stanDictVar['tau_tilde_sigma']#1

            alpha_mu = stanDictVar['alpha_mu']#0
            alpha_sigma = stanDictVar['alpha_sigma']#2

            stan_code = '''
                        data {
                            int<lower=2> K;
                            int<lower=0> N;
                            int<lower=1> D;
                            int<lower=1,upper=K> y[N];
                            row_vector[D] x[N];
                        }
                        parameters {
                            vector[D] beta_tilde;
                            vector<lower=0>[D] lambda;
                            real<lower=0> tau_tilde;

                            ordered[K-1] c;
                            real alpha;
                        }
                        model {
                            vector[D] beta = beta_tilde .* lambda * tau_tilde;

                            beta_tilde ~ normal('''+str(beta_tilde_mu)+''', '''+str(beta_tilde_sigma)+''');
                            lambda ~ cauchy('''+str(lambda_mu)+''', '''+str(lambda_sigma)+''');
                            tau_tilde ~ cauchy('''+str(tau_tilde_mu)+''', '''+str(tau_tilde_sigma)+''');

                            alpha ~ normal('''+str(alpha_mu)+''', '''+str(alpha_sigma)+''');

                            for (n in 1:N)
                                y[n] ~ ordered_logistic(x[n] * beta + alpha, c);
                        }
                        '''
        elif priorType == 'Finnish_horseshoe':
            mZero = stanDictVar['m0']#10
            slab_scale = stanDictVar['slab_scale']#3
            slab_df = stanDictVar['slab_df']#25

            beta_tilde_mu = stanDictVar['beta_tilde_mu']#0
            beta_tilde_sigma = stanDictVar['beta_tilde_sigma']#1

            lambda_mu = stanDictVar['lambda_mu']#0
            lambda_sigma = stanDictVar['lambda_sigma']#1

            tau_tilde_mu = stanDictVar['tau_tilde_mu']#0
            tau_tilde_sigma = stanDictVar['tau_tilde_sigma']#1
            
            alpha_mu = stanDictVar['alpha_mu']#0
            alpha_sigma = stanDictVar['alpha_sigma']#2
            
            stan_code = '''
                        data {
                            int<lower=2> K;
                            int<lower=0> N;
                            int<lower=1> D;
                            int<lower=1,upper=K> y[N];
                            row_vector[D] x[N];
                        }
                        transformed data {
                            real m0 = '''+str(mZero)+''';           // Expected number of large slopes
                            real slab_scale = '''+str(slab_scale)+''';    // Scale for large slopes
                            real slab_scale2 = square(slab_scale);
                            real slab_df = '''+str(slab_df)+''';      // Effective degrees of freedom for large slopes
                            real half_slab_df = 0.5 * slab_df;
                        }
                        parameters {
                            vector[D] beta_tilde;
                            vector<lower=0>[D] lambda;
                            real<lower=0> c2_tilde;
                            real<lower=0> tau_tilde;
                            
                            ordered[K-1] c;
                            real alpha;
                        }
                        transformed parameters {
                            vector[D] beta;
                            {
                                real tau0 = (m0 / (D - m0)) * (1.0 / sqrt(1.0 * N));
                                real tau = tau0 * tau_tilde; // tau ~ cauchy(0, tau0)

                                // c2 ~ inv_gamma(half_slab_df, half_slab_df * slab_scale2)
                                // Implies that marginally beta ~ student_t(slab_df, 0, slab_scale)
                                real c2 = slab_scale2 * c2_tilde;

                                vector[D] lambda_tilde = sqrt(c2 * square(lambda) ./ (c2 + square(tau) * square(lambda)));

                                // beta ~ normal(0, tau * lambda_tilde)
                                beta = tau * lambda_tilde .* beta_tilde;
                            }
                        }
                        model {
                            beta_tilde ~ normal('''+str(beta_tilde_mu)+''', '''+str(beta_tilde_sigma)+''');
                            lambda ~ cauchy('''+str(lambda_mu)+''', '''+str(lambda_sigma)+''');
                            tau_tilde ~ cauchy('''+str(tau_tilde_mu)+''', '''+str(tau_tilde_sigma)+''');
                            c2_tilde ~ inv_gamma(half_slab_df, half_slab_df);

                            alpha ~ normal('''+str(alpha_mu)+''', '''+str(alpha_sigma)+''');

                            for (n in 1:N)
                                y[n] ~ ordered_logistic(x[n] * beta + alpha, c);
                        }
                        '''
        elif priorType == 'normBeta':
            beta_mu = stanDictVar['beta_mu']#0
            beta_sigma = stanDictVar['beta_sigma']#10

            alpha_mu = stanDictVar['alpha_mu']#0
            alpha_sigma = stanDictVar['alpha_sigma']#2

            stan_code = '''
                        data {
                            int<lower=2> K;
                            int<lower=0> N;
                            int<lower=1> D;
                            int<lower=1,upper=K> y[N];
                            row_vector[D] x[N];
                        }
                        parameters {
                            vector[D] beta;
                            ordered[K-1] c;
                            real alpha;
                        }
                        model {
                            beta ~ normal('''+str(beta_mu)+''', '''+str(beta_sigma)+''');
                            alpha ~ normal('''+str(alpha_mu)+''', '''+str(alpha_sigma)+''');

                            for (n in 1:N)
                                y[n] ~ ordered_logistic(x[n] * beta + alpha, c);
                        }
                        '''
        elif priorType == 'uniformBeta':
            alpha_mu = stanDictVar['alpha_mu']#0
            alpha_sigma = stanDictVar['alpha_sigma']#2

            stan_code = '''
                        data {
                            int<lower=2> K;
                            int<lower=0> N;
                            int<lower=1> D;
                            int<lower=1,upper=K> y[N];
                            row_vector[D] x[N];
                        }
                        parameters {
                            vector[D] beta;
                            ordered[K-1] c;
                            real alpha;
                        }
                        model {
                            alpha ~ normal('''+str(alpha_mu)+''', '''+str(alpha_sigma)+''');

                            for (n in 1:N)
                                y[n] ~ ordered_logistic(x[n] * beta + alpha, c);
                        }
                        '''
        
        data_dict = {'x':teamData,\
                     'y':rankData,\
                     'K':rankData.shape[0],\
                     'N':teamData.shape[0],\
                     'D':teamData.shape[1]}
        
        stan_model = pystan.StanModel(model_code=stan_code)
        fit_sample = stan_model.sampling(data=data_dict,\
                                         iter=nIter,\
                                         chains=nChains,
                                         n_jobs=nJobs)
        
        fitSampling_DF = fit_sample.to_dataframe()

        s = fit_sample.summary()
        fitSummary_DF = pd.DataFrame(s['summary'],\
                                     columns=s['summary_colnames'],\
                                     index=s['summary_rownames'])

        # Rename beta columns with corresponding y column names
        beta_shape = fit_sample.extract()['beta'].shape

        if beta_shape[1] == teamData.shape[1]:
            betaDict = {}
        
            for i in range(beta_shape[1]):    
                betaDict['beta['+str(i+1)+']'] = teamData.columns[i]
            
        else:
            return 'Number of beta sampling columns ('+str(beta_shape[1])+') != colNames ('+str(teamData.shape[1])+')'
    else:
        return 'X matrix and Y matrix do not have the same number of rows'

    return fitSampling_DF,fitSummary_DF,betaDict

def normalityTests(data,\
                   alpha=0.05):

    try:
        testResult = ''
        normBool = True

        # Shapiro-Wilk test for normality
        shapiro_stat, shapiro_p = shapiro(data)

        if shapiro_p > alpha:
            testResult += 'Shapiro-Wilk test fails to reject H_0 (stat=%.3f, p=%.3f)\n' % (shapiro_stat, shapiro_p)
        else:
            testResult += 'Shapiro-Wilk test rejects H_0 (stat=%.3f, p=%.3f)\n' % (shapiro_stat, shapiro_p)
            normBool = False
        
        # D'Agostino’s K^2 test for normality
        d_agostino_stat, d_agostino_p = normaltest(data)

        if d_agostino_p > alpha:
            testResult += 'D\'Agostino’s K^2 test fails to reject H_0 (stat=%.3f, p=%.3f)\n' % (d_agostino_stat, d_agostino_p)
        else:
            testResult += 'D\'Agostino’s K^2 test rejects H_0 (stat=%.3f, p=%.3f)\n' % (d_agostino_stat, d_agostino_p)
            normBool = False
        
        # Anderson-Darling Test for normality
        anderson_result = anderson(data)

        for i in range(len(anderson_result.critical_values)):
            sl = anderson_result.significance_level[i]
            cv = anderson_result.critical_values[i]

            if anderson_result.statistic < anderson_result.critical_values[i]:
                testResult += 'Anderson-Darling test fails to reject H_0 (sig. level=%.3f, crit. value=%.3f)\n' % (sl, cv)
            else:
                testResult += 'Anderson-Darling test rejects H_0 (sig. level=%.3f, crit. value=%.3f)\n' % (sl, cv)
                normBool = False

        return testResult,normBool
    except:
        return None

def oneSampleTest(data,\
                  alpha=0.05,\
                  dictVals={'axis':0,\
                            'nan_policy':'propagate',\
                            'zero_method':'wilcox',\
                            'corrBool':False,\
                            'mode':'auto'}):
    try:
        normResult = normalityTests(data,\
                                    alpha)
        
        if not (normResult is None):
            normBool = normResult[1]

            if normBool:
                axis = dictVals['axis']
                nan_policy = dictVals['nan_policy']

                stat, pvalue = ttest_1samp(data,\
                                           0,\
                                           axis=axis,\
                                           nan_policy=nan_policy)
                testType = 'Student\'s t-test'
            else:
                zero_method = dictVals['zero_method']
                corrBool = dictVals['corrBool']
                mode = dictVals['mode']

                stat, pvalue = wilcoxon(data,\
                                        zero_method=zero_method,\
                                        correction=corrBool,\
                                        mode=mode)
                testType = 'Wilcoxon Signed-Rank Test'
        
        else:
            testType = None
            stat = None
            pvalue = None

        return testType,stat,pvalue
    except:
        return None