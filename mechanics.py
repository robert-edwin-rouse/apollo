"""
Machine learning & data science utility functions

@author: robert-edwin-rouse
"""

import numpy as np
import matplotlib.pyplot as plt


def textstyle(fontsize=20, family='serif', font='Times New Roman'):
    '''
    Sets the global font styles for plotting functions

    Parameters
    ----------
    fontsize : Float, optional
        Desired font size. The default is 20.
    family : String, optional
        Font family library containing the desired font. The default is 'serif'.
    font : String, optional
        Desired font. The default is 'Times New Roman'.

    Returns
    -------
    None.

    '''
    plt.rcParams['font.size'] = fontsize
    plt.rcParams['font.family'] = family
    fontlibrary = str('font.' + family)
    plt.rcParams[fontlibrary] = [font]


def featurelocator(df, features):
    '''
    Identifies the column numbers for features from a dataframe
    for use with indexing the array form of that dataframe

    Parameters
    ----------
    df : Pandas dataframe
        Pandas dataframe of all input and output information
    features : List
        List of target variables or features.

    Returns
    -------
    array_indices : List
        List of indices for slicing the converted array.
    '''
    array_indices = [df.columns.get_loc(f) for f in features]
    return array_indices


def normalise(df, feature, norm_dict={}, write_cache=True):
    '''
    Normalises the feature columns of a dataframe, with the option
    to retain a cache of the normalisation parameters for use on additional
    datasets.    
    
    Parameters
    ----------
    df : Pandas dataframe
        Dataframe containing columns of variables to be normalised
    feature : String
        Name of feature column to be normalised
    norm_dict : Dictionary
        Dictionary in which normalisation cache parameters are stored
    write_cache : Boolean
        Determines whether or not the cache key values will be overwritten

    Returns
    -------
    array_indices : List
        The input feature column normalised with a dictionary key value entry
        made containing all normalisation parameters.
    '''
    if write_cache == True:
        favg = np.mean(df[feature])
        fmax = np.max(df[feature])
        fmin = np.min(df[feature])
        cachelist = [favg, fmax, fmin]
        norm_dict[feature] = cachelist
        return(df[feature] - favg)/(fmax-fmin)
    elif write_cache == False:
        try:
            cache = norm_dict[feature]
            return(df[feature] - cache[0])/(cache[1]-cache[2])
        except:
            raise KeyError('Normalisation cache specified incorrectly')


def best_fit(x,y):
    '''
    Fits a line of best fit to data via linear regression for a
    dataset in 2 dimensions.
    
    Parameters
    ----------
    xs : Array
        x data.
    ys : Array
        y data.

    Returns
    -------
    m : Float
        The gradient for the line of best fit
    c : Float
        The intercept for the line of best fit
    '''
    m = ((np.mean(x)*np.mean(y) - np.mean(x*y)) /
         (np.mean(x)*np.mean(x) - np.mean(x*x)))
    c = np.mean(y) - m*np.mean(x)
    return m, c


def string_to_list(l, numeric=True):
    '''
    Takes an imported string of a list and turns it back into a list.

    Parameters
    ----------
    l : String
        String of a list.
    numeric : Boolean, optional
        Indicates whether the list needs to be numerical or can be left as
        a list of strings. The default is True.

    Returns
    -------
    List
        List of string or numeric data types.
    '''
    l = l.strip('][').split(', ')
    if numeric==True:
        return [float(x) for x in l]
    else:
        return l