"""
Script to create datafiles for lumped catchment streamflow regression, combining
meteorological and hydrological data.

In order to run this script, a database in csv format of catchments along with
their respective streamflow datafiles, also in csv format, will be required.
Also required is meteorological analysis data, which we recommend is stored in
the netcdf format, accessed using xarray.

@author: robertrouse
"""

import pandas as pd
import numpy as np
import xarray as xr
import datetime as dt
import geopandas as gp
from apollo import mechanics as ma
from apollo import osgconv as osg


def rename(df):
    '''
    Dictionary based renaming of columns within a dataframe from ECMWF
    nomenclature to plain language.

    Parameters
    ----------
    df : Pandas dataframe
        Original dataframe of variables pulled from ERA5.

    Returns
    -------
    df : Pandas dataframe
        Dataframe with renamed columns for human readability.
    '''
    df = df.rename(columns={'time':'Date','tp':'Rain',
                            't':'Temperature','r':'Humidity',
                            'u':'U Windspeed','v':'V Windspeed',
                            'swvl1':'Soil Moisture 1',
                            'swvl2':'Soil Moisture 2',
                            'swvl3':'Soil Moisture 3',
                            'swvl4':'Soil Moisture 4'})
    return df


def weather_shift(df, variable, ndays, past=True):
    '''
    Creates additional columns by copying meteorological variables and
    shifting them back or forward in time for a given number of steps,
    creating rows of data with the required antecedent record that can be
    passed directly into a model.

    Parameters
    ----------
    xf : Pandas dataframe
        Dataframe of variables to be shifted in time.
    variable : String
        Name of the feature column to be shifted.
    ndays : Integer
        Number of days, or timesteps, to apply the shift.
    past : Boolean, optional
        Applying either a rearward or forward looking shift.
        The default is True.

    Returns
    -------
    xf : Pandas dataframe
        Dataframe with time shifted variables in each row.
    '''
    if past == True:
        for i in range (1, ndays):
            colname = str(variable) + '-{0}'.format(i)
            df[colname] = df[variable].shift(+i)
    else:
        for i in range (1, ndays):
            colname = str(variable) + '+{0}'.format(i)
            df[colname] = df[variable].shift(-i)
    return df


class hydrobase():
    def __init__(self, station, flowpath, boundarypath):
        '''
        Initialises a class instance of a streamflow database.
        
        Parameters
        ----------
        station : String
            Gauging station number, keyed to flow data files.
        flowpath : String
            File path for the flow data file.
        boundarypath : String
            File path for the .shp catchment boundary file.  Note that the
            .shx file must also be present in the same location.

        Returns
        -------
        None.
        '''
        self.station = station
        self.flowpath = flowpath
        self.flow = pd.read_csv(flowpath)
        self.flow = self.flow.drop(self.flow.columns[2], axis=1)
        self.flow = self.flow.drop(self.flow.index[0:19])
        self.flow.columns = ['Date', 'Flow']
        self.flow['Date'] = pd.to_datetime(self.flow['Date'],
                                           format='%Y-%m-%d').dt.date
        self.flow['Flow'] = self.flow['Flow'].astype(float)
        self.boundarypath = boundarypath
        self.boundary = gp.read_file(self.boundarypath)
        self.points = self.boundary.centroid
        self.lat, self.lon = osg.BNG_2_latlon(self.points.x[0],
                                              self.points.y[0])
        
    def meteorological_extraction(self, domain_data):
        '''
        Extracts meteorological data from the domain datafiles using xarray
        and interpolates across the spatial dimensions to obtain a single
        time series of the meteorological variables.

        Parameters
        ----------
        domain_data : Xarray
            Array of spatio-temporally distributed variables.

        Returns
        -------
        local_data : Xarray
            Interpolated variables at the centroid coordinates.
        '''
        local_data = domain_data.interp(longitude=self.lon, latitude=self.lat)
        local_data = local_data.to_dataframe().reset_index()
        return local_data
    
    def flow_meteorolgy_combine(self, domain_weather, surface_data, days):
        '''
        Takes the standard CEH flow file format and combines it with
        meteorological data interpolated at the centroid of the catchment.

        Parameters
        ----------
        domain_weather : Xarray opened netcdf file
            Meteorological, or other, netcdf files opened using xarray.
        surface_data : Xarray opened netcdf file
            Soil moisture, or other, surface netcdf files opened using xarray
        days : Integer
            Number of days needed for antecedent record.

        Returns
        -------
        combined : Pandas dataframe
            A single dataframe combining all input meteorological and output
            streamflow variables.
        '''
        weather = self.meteorological_extraction(domain_weather)
        surface = self.meteorological_extraction(surface_data)
        weather = rename(weather)
        surface = rename(surface)
        weather['Rain'] = weather['Rain']*1000*24
        weather['Date'] = pd.to_datetime(weather['Date'],
                                         format='%Y-%m-%d').dt.date
        surface['Date'] = pd.to_datetime(surface['Date'],
                                         format='%Y-%m-%d').dt.date
        weather = weather.drop(['longitude', 'latitude'], axis=1)
        surface = surface.drop(['longitude', 'latitude'], axis=1)
        weather['Resultant Windspeed'] = (weather['U Windspeed']**2
                                          + weather['V Windspeed']**2)**(1/2)
        for f in ['Rain','Temperature','Resultant Windspeed','Humidity']:
            weather = weather_shift(weather, f, days)
            for window in [28, 90, 180]:
                ma.stat_roller(weather, f, window, method='mean')
        combined = pd.merge(weather, surface, on='Date')
        combined = pd.merge(self.flow, combined, how='inner', on='Date')
        combined = combined.drop(combined.index[0:179])
        return combined
    
    def output_file(self, domain_weather, surface_data, days):
        '''
        Applies the meteorological extraction and dataset combination functions
        and returns a single combined dataframe which is then exported as a 
        lumped regression .csv file.

        Parameters
        ----------
        domain_weather : Xarray opened netcdf file
            Meteorological, or other, netcdf files opened using xarray.
        surface_data : Xarray opened netcdf file
            Soil moisture, or other, surface netcdf files opened using xarray
        days : Integer
            Number of days needed for antecedent record.

        Returns
        -------
        None.
        '''
        outdf = self.flow_meteorolgy_combine(domain_weather, surface_data, days)
        outpath = str(self.station) + '_lumped.csv'
        outdf.to_csv(outpath, index=True)
