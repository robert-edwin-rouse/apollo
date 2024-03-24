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
import mechanics as me
import centroid as cr


def rename(df):
    df = df.rename(columns={'tp':'Rain','t':'Temperature',
                        'u':'U Windspeed','v':'V Windspeed','r':'Humidity',
                        'swvl1':'Soil Moisture 1','swvl2':'Soil Moisture 2',
                        'swvl3':'Soil Moisture 3','swvl4':'Soil Moisture 4'})
    return df


def weathershift(xf, variable, ndays, past=True):
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
        
    def meteorological_extraction(self, global_weather, m='cubic'):
        local_weather = global_weather.interp(longitude=self.lon,
                                              latitude=self.lat, method=m)
        local_weather = local_weather.to_dataframe().reset_index()
        return local_weather
    
    def flow_meteorolgy_combine(self, era_data, days):
        weather = self.meteorological_extraction(era_data)
        weather = rename(weather)
        weather['Resultant Windspeed'] = (weather['U Windspeed']**2 +
                                          weather['V Windspeed']**2)**(1/2)
        for f in ['Rain','Temperature','Resultant Windspeed','Humidity']:
            weather = weathershift(weather, f, days)
        weather = pd.to_datetime(weather['Date'], format='%Y-%m-%d').dt.date
        combined = pd.merge(self.flow, weather, how='inner', on='Date')
        return combined
    
    def output_file(self, era_data, days):
        outdf = self.flow_meteorolgy_combine(era_data, days)
        outpath = self.station + '_lumped.csv'
        outdf.to_csv(outpath, index=True)

pd.merge

rain = xr.open_dataset('Daily Precipitation Full.nc')
pressure = xr.open_dataset('test.nc')
# surface = xr.open_dataset('soiltest.nc')
global_weather = xr.merge([rain, pressure], join='inner')
db = pd.read_csv('CDTest.csv')
test = hydrobase(db.loc[0][0], db.loc[0][3], db.loc[0][4], db.loc[0][5])
cache = test.meteorological_extraction(global_weather)