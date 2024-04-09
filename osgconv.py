"""
Script to convert from the British National Grid coordinate system to the
WGS84 latitudinal-longitudinal coordinate system, based on the information
contained within the guidance from the UK Ordnance Survey:
<https://www.ordnancesurvey.co.uk/documents/resources/
guide-coordinate-systems-great-britain.pdf>,
archived here: https://archive.md/7F2kq

@author: robert-edwin-rouse
"""

import math as m


def parameter_set_1(a, b):
    '''
    Calculates the first set of parameters, eccentricity and n, 
    from a set of ellipsoid parameters for a given datum.
    
    Parameters
    ----------
    a : Float
        Semi-major axis.
    b : Float
        Semi-minor axis.

    Returns
    -------
    e2 : Float
        Eccentricity squared.
    n : Float
        Ellipsoid parameter n.
    '''
    e2 = (a**2 - b**2)/(a**2)
    n = (a-b)/(a+b)
    return e2, n


def parameter_set_2(ϕ, a, F, e2):
    '''
    Calculates the second set of parameters, ν, ρ, and η, from the converged
    latitudinal and ellipsoid parameters for a given datum.
    
    Parameters
    ----------
    ϕ : Float
        Longitudinal coordinate.
    a0 : Float
        Semi-major axis.
    F0 : Float
        Scale factor on central meridian.
    e2 : Float
        Eccentricity Squared.

    Returns
    -------
    ν : Float
        Conversion parameter, ν.
    ρ : Float
        Conversion parameter, ρ.
    η : Float
        Conversion parameter, η.
    '''
    ν = a * F / (1 - e2 * m.sin(ϕ)**2)**(0.5)
    ρ = a * F * (1 - e2)/((1 - e2 * m.sin(ϕ)**2)**(3/2))
    η = ν/ρ - 1
    return ν, ρ, η


def f_M(ϕ, ϕ0, n, b, F):
    '''
    Computation of parameter M, using an iteratively updated value of 
    the latitudinal parameter, ϕ,
    
    Parameters
    ----------
    ϕ : Float
        Iteratively updated latitude.
    ϕ0 : Float
        Initial latitude.
    a : Float
        Semi-major axis.
    b : Float
        Semi-minor axis.
    F0 : Float
        Scale factor on central meridian.

    Returns
    -------
    M : Float
        Iterative parameter, M.
    '''
    Δϕ = ϕ - ϕ0
    Σϕ = ϕ + ϕ0
    M = b * F * ((1 + n + 5/4*n**2 + 5/4*n**3) * Δϕ
                 - (3*n + 3*n**2 + 21/8*n**3) * m.sin(Δϕ) * m.cos(Σϕ)
                 + (15/8 * (n**2 + n**3) * m.sin(2*Δϕ) * m.cos(2*Σϕ))
                 - (35/24 * n**3 * m.sin(3*Δϕ) * m.cos(3*Σϕ)))
    return M


def BNG_2_latlon(E, N):
    '''
    Converts British National Grid Easting and Northing coordinate pair to a
    latitude/longitude coordinate pair using the WGS84 elipsoid

    Parameters
    ----------
    E : Float
        Easting coordinate to be converted.
    N : Float
        Northing coordinate to be converted.

    Returns
    -------
    ϕ : Float
        Latitude coordinate.
    λ : Float
        Longitude coordinate.

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
    while abs(N-N0-M)>=1e-5:
        prime = (N-N0-M)/(a0*F0) + prime
        M = f_M(prime, ϕ0, n, b0, F0)
    
    ν, ρ, η = parameter_set_2(prime, a0, F0, e2)
    
    tn = m.tan(prime)
    sc = 1/m.cos(prime)

    c1 = tn/(2*ρ*ν)
    c2 = tn/(24*ρ*ν**3) * (5 + 3*tn**2 + η**2 * (1 - 9*tn**2))
    c3 = tn/(720*ρ*ν**5) * (61 + tn**2*(90 + 45 * tn**2))
    d1 = sc/ν
    d2 = sc/(6*ν**3) * (ν/ρ + 2*tn**2)
    d3 = sc/(120*ν**5) * (5 + tn**2*(28 + 24*tn**2))
    d4 = sc/(5040*ν**7) * (61 + tn**2*(662 + tn**2*(1320 + tn**2*720)))
    ED = E - E0
    ϕ = m.degrees(prime + ED**2 * (-c1 + ED**2*(c2 - c3*ED**2)))
    λ = m.degrees(λ0 + ED * (d1 + ED**2*(-d2 + ED**2*(d3 - d4*ED**2))))
    return ϕ, λ