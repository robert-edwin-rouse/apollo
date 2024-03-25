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
from apollo import mechanics as me
from apollo import centroid as cr


def rename(df):
    df = df.rename(columns={'time':'Date','tp':'Rain','t':'Temperature',
                        'u':'U Windspeed','v':'V Windspeed','r':'Humidity',
                        'swvl1':'Soil Moisture 1','swvl2':'Soil Moisture 2',
                        'swvl3':'Soil Moisture 3','swvl4':'Soil Moisture 4'})
    return df


def weather_shift(xf, variable, ndays, past=True):
    if past == True:
        for i in range (1, ndays):
            colname = str(variable) + '-{0}'.format(i)
            xf[colname] = xf[variable].shift(+i)
    else:
        for i in range (1, ndays):
            colname = str(variable) + '+{0}'.format(i)
            xf[colname] = xf[variable].shift(-i)
    return xf


class hydrobase():
    def __init__(self, station, flowpath, gridfile, gridsquare):
        self.station = station
        self.flowpath = flowpath
        self.flow = pd.read_csv(flowpath)
        self.flow = self.flow.drop(self.flow.columns[2], axis=1)
        self.flow = self.flow.drop(self.flow.index[0:19])
        self.flow.columns = ['Date', 'Flow']
        self.flow['Date'] = pd.to_datetime(self.flow['Date'],
                                        format='%Y-%m-%d').dt.date
        self.flow['Flow'] = self.flow['Flow'].astype(float)
        self.gridfile = gridfile
        self.gridsquare = me.string_to_list(gridsquare)
        self.centroid = cr.Centroid(gridfile)
        self.lon, self.lat = self.centroid.lat_lon(self.gridsquare[0],
                                                        self.gridsquare[1],
                                                        self.gridsquare[2],
                                                        self.gridsquare[3],)
        
    def meteorological_extraction(self, domain_data):
        local_data = domain_data.interp(longitude=self.lon, latitude=self.lat)
        local_data = local_data.to_dataframe().reset_index()
        return local_data
    
    def flow_meteorolgy_combine(self, domain_weather, surface_data, days):
        weather = self.meteorological_extraction(domain_weather)
        surface = self.meteorological_extraction(surface_data)
        weather = rename(weather)
        surface = rename(surface)
        weather['Date'] = pd.to_datetime(weather['Date'],
                                         format='%Y-%m-%d').dt.date
        surface['Date'] = pd.to_datetime(surface['Date'],
                                         format='%Y-%m-%d').dt.date
        weather['Resultant Windspeed'] = (weather['U Windspeed']**2 +
                                          weather['V Windspeed']**2)**(1/2)
        for f in ['Rain','Temperature','Resultant Windspeed','Humidity']:
            weather = weather_shift(weather, f, days)
        combined = pd.merge(weather, surface, how='inner', on='Date')
        combined = pd.merge(self.flow, combined, how='inner', on='Date')
        return combined
    
    def output_file(self, era_data, days):
        outdf = self.flow_meteorolgy_combine(era_data, days)
        outpath = self.station + '_lumped.csv'
        outdf.to_csv(outpath, index=True)
