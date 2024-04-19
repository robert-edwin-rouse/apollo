'''
Provides utility functions for the hydrological machine learning study on
soil moisture proxies.

Utility functions include normalisation, feature detection, and standard
plotting functions for visualisation of the results as per the publication.

'''

import numpy as np
import datetime as dt
import matplotlib.dates as mdt
import matplotlib.ticker as mtk
import matplotlib.pyplot as plt


def year_plot(maxflow, df, y_pred, y_obsv, year, colour1='cadetblue',
              colour2='darkseagreen'):
    '''
    Generates a scatter plot of observations against predictions with an
    indicator line of perfect fit.    

    Parameters
    ----------
    maxflow : Float
        Maximum flow for scaling the y axis
    df : Pandas dataframe
        Pandas dataframe with observations, predictions, and date columns
    y_pred : String
        Name of the predicted flow column
    y_obsv : String
        Name of the observed flow column
    year : Integer
        Target year to be plotted as a time series
    colour1 : String, optional
        Predicted time series colour. The default is 'cadetblue'.
    colour2 : String, optional
        Observed time series colour. The default is 'darkseagreen'.

    Returns
    -------
    None.

    '''
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(df['Date'], df[y_pred], colour1, lw=3.2)
    ax.plot(df['Date'], df[y_obsv], colour2, lw=3.2, ls='--')
    ax.set_xlabel('Date')
    ax.set_ylabel('Flow (m'+r'$^3$'+'s'+r'$^{-1}$'+')')
    ax.set_xlim([dt.date(year, 1, 1), dt.date(year, 12, 31)])
    ax.set_ylim(0,maxflow)
    ax.xaxis.set_major_locator(mdt.MonthLocator())
    ax.xaxis.set_major_formatter(mdt.DateFormatter('%b'))
    ax.yaxis.set_major_locator(mtk.MaxNLocator(5))
    ax.legend(['Prediction', 'Actual'], loc='upper left')
    ax.grid(c='black', ls='dotted', lw=0.5)
    plt.show()


def scatter_plot(maxflow, df, pred, obsv, colour='steelblue', marker='*'):
    '''
    Generates a scatter plot of observations against predictions with an
    indicator line of perfect fit.
    
    Parameters
    ----------
    maxflow : Float
        Maximum flow for scaling the y axis
    df : Pandas dataframe
        Pandas dataframe with observations, predictions, and date columns
    pred : String
        Name of the predicted flow column
    obsv : String
        Name of the observed flow column
    colour : String, optional
        Scatter point colours. The default is 'steelblue'.
    marker : String, optional
            Scatter point colours. The default is 'steelblue'.

    Returns
    -------
    None.

    '''
    xyline = np.linspace(0, maxflow, maxflow)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(df[pred], df[obsv], marker=marker, s=4, c=colour)
    ax.plot(xyline, xyline, c='black', lw=1)
    ax.set_xlabel('Predicted Flow (m'+r'$^3$'+'s'+r'$^{-1}$'+')')
    ax.set_ylabel('Observed Flow (m'+r'$^3$'+'s'+r'$^{-1}$'+')')
    ax.set_xlim([0, maxflow])
    ax.set_ylim([0, maxflow])
    ax.xaxis.set_major_locator(mtk.MaxNLocator(5))
    ax.yaxis.set_major_locator(mtk.MaxNLocator(5))
    plt.show()


def rainflow_plot(maxflow, maxrain, df, flow, rain, year, colour1='cadetblue',
               colour2='darkseagreen'):
    '''
    Generates a scatter plot of observations against predictions with an
    indicator line of perfect fit.

    Parameters
    ----------
    maxflow : Float
        Maximum flow for scaling the y axis
    maxrain : Float
        Maximum rain for scaling the y axis
    df : Pandas dataframe
        Pandas dataframe with observations, predictions, and date columns
    flow : String
        Name of the observed flow column
    rain : String
        Name of the observed rain column
    year : Integer
        Target year to be plotted as a time series
    colour1 : String, optional
        Predicted time series colour. The default is 'cadetblue'.
    colour2 : String, optional
        Observed time series colour. The default is 'darkseagreen'.

    Returns
    -------
    None.

    '''
    fig, ax1 = plt.subplots(figsize=(16, 8))
    ax1.set_xlim([dt.date(year, 1, 1), dt.date(year, 12, 31)])
    ax1.set_xlabel('Date')
    ax1.xaxis.set_major_locator(mdt.MonthLocator())
    ax1.xaxis.set_major_formatter(mdt.DateFormatter('%b'))
    ax1.set_ylim(0,maxflow)
    ax1.set_ylabel('Flow (m'+r'$^3$'+'s'+r'$^{-1}$'+')')
    ax1.yaxis.set_major_locator(mtk.MaxNLocator(5))
    ax1.grid(c='black', ls='dotted', lw=0.5)
    ax1.plot(df['Date'], df[flow], colour2, lw=3.2, label='Flow')
    ax1.plot(np.nan, colour1, lw=3.2, label='Precipitation', ls='--')
    ax2 = ax1.twinx()
    ax2.set_ylabel('Precipitation (mm)')
    ax2.set_ylim(maxrain,0)
    ax2.plot(df['Date'], df[rain], colour1, lw=3.2, ls='--')
    ax1.legend(loc=0, bbox_to_anchor=(0.25,0.8))
    plt.show()