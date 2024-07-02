"""
Machine learning & data science performance metrics

@author: robert-edwin-rouse
"""

import numpy as np


def RMSE(y_o, y_p):
    '''
    Function to evalate the root mean squared error
    between a set of observations and predictions
    
    Parameters
    ----------
    y_o : Float, Numpy Array, or Pandas DataFrame Column
        Set of observations, y
    y_p : Float, Numpy Array, or Pandas DataFrame Column
        Set of predictions, y'
        
    Returns
    -------
    rmse : Float
        Root Mean Squared Error
    '''
    total = (((y_o - y_p)**2)/len(y_o))
    rmse = sum(total)**0.5
    return rmse


def MPRE(y_o, y_p):
    '''
    Function to evalate the mean percent relative error
    between a set of observations and predictions
    
    Parameters
    ----------
    y_o : Float, Numpy Array, or Pandas DataFrame Column
        Set of observations, y
    y_p : Float, Numpy Array, or Pandas DataFrame Column
        Set of predictions, y'
        
    Returns
    -------
    rmse : Float
        Relative Bias
    '''
    total = abs((y_o - y_p)/y_o)
    mpre = 100*sum(total)/len(y_o)
    return mpre


def RB(y_o, y_p):
    '''
    Function to evalate the relative bias
    between a set of observations and predictions
    
    Parameters
    ----------
    y_o : Float, Numpy Array, or Pandas DataFrame Column
        Set of observations, y
    y_p : Float, Numpy Array, or Pandas DataFrame Column
        Set of predictions, y'
        
    Returns
    -------
    rmse : Float
        Relative Bias
    '''
    total = (y_o - y_p)/y_o
    rb = sum(total)/len(y_o)
    return rb


def R2(y_o, y_p):
    '''
    Function to evalate the r2 value between
    a set of observations and predictions
    
    Parameters
    ----------
    y_o : Float, Numpy Array, or Pandas DataFrame Column
        Set of observations, y
    y_p : Float, Numpy Array, or Pandas DataFrame Column
        Set of predictions, y'
        
    Returns
    -------
    r2 : Float 
        R2
    '''
    cache1 = ((y_o - y_p)**2)
    mu = np.mean(y_o)
    cache2 = ((y_o - mu)**2)
    r2 = 1 - (sum(cache1))/(sum(cache2))
    return r2


def KGE(y_o, y_p):
    '''
    Function to evalate the Kling-Gupta Efficiency for
    a set of observations and predictions
    
    Parameters
    ----------
    y_o : Float, Numpy Array, or Pandas DataFrame Column
        Set of observations, y
    y_p : Float, Numpy Array, or Pandas DataFrame Column
        Set of predictions, y'
        
    Returns
    -------
    kge : Float
        Kling-Gupta Efficiency
    '''
    n = len(y_o)
    r = (n*sum(y_o*y_p) - sum(y_o)*sum(y_p)) / (
        (n*sum(y_o*y_o) - sum(y_o)*sum(y_o)) *
        (n*sum(y_p*y_p) - sum(y_p)*sum(y_p)))**(0.5)
    alpha = np.mean(y_p)/np.mean(y_o)
    beta = np.std(y_p)/np.std(y_o)
    kge = 1 - ((r-1)**2 + (alpha-1)**2 + (beta-1)**2)**(0.5)
    return kge


def RE(y_o, y_p, psi):
    '''
    Function to evalate the reflective error
    between a set of observations and predictions
    
    Parameters
    ----------
    y_o : Float, Numpy Array, or Pandas DataFrame Column
        Set of observations, y
    y_p : Float, Numpy Array, or Pandas DataFrame Column
        Set of predictions, y'
        
    Returns
    -------
    r_rmse : Float
        Reflective Root Mean Squared Error
    '''
    cache1 = ((y_o - y_p)**2)
    re = ((sum(cache1 * psi))/(sum(cache1)))**(0.5)
    return re


def RELossWeight(u_of_y, alpha, beta, kappa):
    '''
    Function to evalate the weighting to be applied
    elementwise to error terms with 

    Parameters
    ----------
    u_of_y : Float, Numpy Array, or Pandas DataFrame Column
        Probability of y, elementwise, according to
        the distribution fitted to training data
    alpha : Float
        Reflective scaling hyperparameter.
    beta : Float
        Reflective shift hyperparameter.
    kappa : Float
        Global maximum of u_of_y (recommend using calculus to find).

    Returns
    -------
    psi : Float, Numpy Array, or Pandas DataFrame Column
        Reflective weighting to be applied in the loss
        function during network training.

    '''
    psi  = -1 * alpha * (u_of_y/kappa) + beta
    return psi


def RELossFunc(prediction, target, psi):
    '''
    Function to calculate unaggregated loss that can be processed
    using the machine learning library specified by the user

    Parameters
    ----------
    prediction : Float, array, or Tensor
        Machine learning algorithm output.
    target :  Float, array, or Tensor
        Observation to compare the prediction against.
    gamma : Float, array, or Tensor
        Reflective weighting penalty applied elementwise to the
        prediction and target pairs.

    Returns
    -------
    interrim_loss : Float, array, or Tensor
        Unaggregated loss between prediction(s) and target(s).

    '''
    interrim_loss = (((prediction - target)**2) * psi)
    return interrim_loss