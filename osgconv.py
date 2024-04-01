"""
Script to convert from the British National Grid coordinate system to the
WGS84 latitudinal-longitudinal coordinate system.

@author: robert-edwin-rouse
"""

import math as m


def parameter_set_1(a, b):
    '''
    
    Parameters
    ----------
    a : TYPE
        DESCRIPTION.
    b : TYPE
        DESCRIPTION.

    Returns
    -------
    e2 : TYPE
        DESCRIPTION.
    n : TYPE
        DESCRIPION.
    '''
    e2 = (a**2 - b**2)/(a**2)
    n = (a-b)/(a+b)
    return e2, n


def parameter_set_2(phi, a0, F0, e2):
    '''

    Parameters
    ----------
    phi : TYPE
        DESCRIPTION.
    a0 : TYPE
        DESCRIPTION.
    F0 : TYPE
        DESCRIPTION.
    e2 : TYPE
        DESCRIPTION.

    Returns
    -------
    rho : TYPE
        DESCRIPTION.
    nu : TYPE
        DESCRIPTION.
    eta2 : TYPE
        DESCRIPTION.
    '''
    nu = a0 * F0 / (1 - e2 * m.sin(phi)**2)**(0.5)
    rho = a0 * F0 * (1 - e2)/((1 - e2 * m.sin(phi)**2)**(3/2))
    eta = nu/rho - 1
    return nu, rho, eta


def f_M(phi, phi0, n, b, F0):
    '''

    Parameters
    ----------
    phi : TYPE
        DESCRIPTION.
    phi0 : TYPE
        DESCRIPTION.
    a : TYPE
        DESCRIPTION.
    b : TYPE
        DESCRIPTION.
    F0 : TYPE
        DESCRIPTION.

    Returns
    -------
    M : TYPE
        DESCRIPTION.
    '''
    delta = phi - phi0
    sigma = phi + phi0
    M = b * F0 * (
            (1 + n + 5/4*n**2 + 5/4*n**3) * delta
            - (3*n + 3*n**2 + 21/8*n**3) * m.sin(delta) * m.cos(sigma)
            + (15/8 * (n**2 + n**3) * m.sin(2*delta) * m.cos(2*sigma))
            - (35/24 * n**3 * m.sin(3*delta) * m.cos(3*sigma))
        )
    return M


def BNG_2_latlon(E, N):
    '''
    

    Parameters
    ----------
    E : TYPE
        DESCRIPTION.
    N : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    a0 = 6377563.396    # Semi-major axis
    b0 = 6356256.909    # Semi-minor axis
    E0 = 400000         # Easting coordinate of true origin
    N0 = -100000        # Northing coordinate of true origin
    ϕ0 = 49             # Longitude coordinate of true origin
    λ0 = -2             # Latitude coordinate of true origin
    F0 = 0.9996012717   # Scale factor on central meridian
    
    e2, n = parameter_set_1(a0, b0)
    ϕ0 = m.radians(ϕ0)
    λ0 = m.radians(λ0)
    
    M, prime = 0, ϕ0
    while abs(N - N0 - M)>=1e-5:
        prime = (N - N0 - M)/(a0*F0) + prime
        M = f_M(prime, ϕ0, n, b0, F0)
    
    nu, rho, eta = parameter_set_2(prime, a0, F0, e2)
    
    tn = m.tan(prime)
    sc = 1/m.cos(prime)

    c1 = tn/(2*rho*nu)
    c2 = tn/(24*rho*nu**3) * (5 + 3*tn**2 + eta**2 * (1 - 9*tn**2))
    c3 = tn/(720*rho*nu**5) * (61 + tn**2*(90 + 45 * tn**2))
    d1 = sc/nu
    d2 = sc/(6*nu**3) * (nu/rho + 2*tn**2)
    d3 = sc/(120*nu**5) * (5 + tn**2*(28 + 24*tn**2))
    d4 = sc/(5040*nu**7) * (61 + tn**2*(662 + tn**2*(1320 + tn**2*720)))
    ED = E - E0
    ϕ = prime + ED**2 * (-c1 + ED**2*(c2 - c3*ED**2))
    λ = λ0 + ED * (d1 + ED**2*(-d2 + ED**2*(d3 - d4*ED**2)))
    return m.degrees(ϕ), m.degrees(λ)