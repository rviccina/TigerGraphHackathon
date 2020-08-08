import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde

def plot_trace(param, param_name='parameter'):
      '''
      Variables for plot_trace
      ---------------------------------------
      keyword         type                 explanation
      ------------    --------------       -----------
      param           np.series/list       data for the parameter being plotted
      param_name      string               name of the parameter being plotted

      output          type                 explanation
      ------------    ------------         -----------
      fig             Figure               plotly figure that contains two subplots: a plot of the samples and a histogram of the samples
      gauss_kde       gaussian_kde         the kernel density class for Gaussian kernel density estimation, see scipy.stats.gaussian_kde
      '''

      # Summary statistics
      mean = np.mean(param)
      median = np.median(param)
      cred_min, cred_max = np.percentile(param, 2.5), np.percentile(param, 97.5)

      # Calculate Kernel Density Estimation (KDE) and relavent statistics
      xRange = list(np.arange(min(param),max(param),0.01))
      gauss_kde = gaussian_kde(param)
      maxY = max(gauss_kde.pdf(xRange))

      # Plotting
      fig = make_subplots(rows=2,\
                        cols=1)

      # Sampling plot
      #--------------------------------------------------------------------
      fig.add_trace(go.Scatter(x=list(range(len(param))),\
                              y=param,\
                              mode='markers',\
                              name='Sampling'),\
                  row=1,\
                  col=1)
      fig.update_xaxes(title_text='samples',\
                        row=1,\
                        col=1)
      fig.update_yaxes(title_text=param_name,\
                        row=1,\
                        col=1)

      # Density Plot
      #--------------------------------------------------------------------
      fig.add_trace(go.Histogram(x=param,\
                                    name='Distribution',\
                                    histnorm='probability density'),\
                  row=2,\
                  col=1)
      fig.add_trace(go.Scatter(x=xRange,\
                              y=gauss_kde.pdf(xRange),\
                              name='Gaussian KDE',\
                              mode='lines'),\
                  row=2,\
                  col=1)
      # Vertical Mean
      fig.add_shape(go.layout.Shape(type='line',\
                                    xref='x',\
                                    yref='y',\
                                    x0=mean,\
                                    y0=0,\
                                    x1=mean,\
                                    y1=maxY,\
                                    line={'dash':'dash',\
                                          'color':'Green'}),
                  row=2,\
                  col=1)
      # Vertical Median
      fig.add_shape(go.layout.Shape(type='line',\
                                    xref='x',\
                                    yref='y',\
                                    x0=median,\
                                    y0=0,\
                                    x1=median,\
                                    y1=maxY,\
                                    line={'dash':'dash',\
                                          'color':'Blue'}),
                  row=2,\
                  col=1)
      # Vertical Lower 95%
      fig.add_shape(go.layout.Shape(type='line',\
                                    xref='x',\
                                    yref='y',\
                                    x0=cred_min,\
                                    y0=0,\
                                    x1=cred_min,\
                                    y1=maxY,\
                                    line={'dash':'dot'}),
                  row=2,\
                  col=1)
      # Vertical Upper 95%
      fig.add_shape(go.layout.Shape(type='line',\
                                    xref='x',\
                                    yref='y',\
                                    x0=cred_max,\
                                    y0=0,\
                                    x1=cred_max,\
                                    y1=maxY,\
                                    line={'dash':'dot'}),
                  row=2,\
                  col=1)
      fig.update_xaxes(title_text=param_name,\
                        row=2,\
                        col=1)
      fig.update_yaxes(title_text='density',\
                        row=2,\
                        col=1)

      # Overall title
      fig.update_layout(title_text='Trace and Posterior Distribution for {}<br>Mean (green): {}, Median (blue), {}'.format(param_name,round(mean,2),round(median,2)))

      return fig,gauss_kde