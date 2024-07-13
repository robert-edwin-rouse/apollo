"""
Thermal utilities for environmental data science projects

@author: robert-edwin-rouse
"""


import numpy as np
import sympy as sp


def wet_bulb(t, h):
    '''
    Function to evaluate the wet bulb temperature from temperature and
    humidity as defined in Stull, R., 2011. Wet-Bulb Temperature from Relative
    Humidity and Air Temperature. Journal of Applied Meteorology and
    Climatology 50, 2267–2269. https://doi.org/10.1175/JAMC-D-11-0143.1

    Parameters
    ----------
    t : Float
        Temperature.
    h : Float
        Relative Humidity.

    Returns
    -------
    wb : Float
        Wet bulb temperature.

    '''
    wb = t * np.arctan(0.151977 * (h + 8.313659)**(1/2)) + \
        0.00391838 * h**(3/2) * np.arctan(0.023101 * h) + \
        np.arctan(t+h) - np.arctan(h - 1.676331) - 4.686035
    return wb


def threshold_wb(h, wb, ini=20):
    '''
    Function to generate temperature from humidity for a given wet bulb
    temperature threshold, as defined in Stull, R., 2011. Wet-Bulb Temperature
    from Relative Humidity and Air Temperature. Journal of Applied Meteorology
    and Climatology 50, 2267–2269. https://doi.org/10.1175/JAMC-D-11-0143.1

    Parameters
    ----------
    h : Float
        Relative Humidity.
    wb : Float
        Wet Bulb Temperature.
    ini : Float, optional
        Initial Guess. The default is 20.

    Returns
    -------
    t : Float
        Temperature.

    '''
    x = sp.symbols("x")
    eq = x * sp.atan(0.151977 * (h + 8.313659)**(1/2)) + \
        0.00391838 * h**(3/2) * sp.atan(0.023101 * h) + \
        sp.atan(x+h) - sp.atan(h - 1.676331) - 4.686035 - wb
    t = sp.nsolve(eq, x, ini)
    return t
