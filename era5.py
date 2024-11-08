"""
Variable names can be found in the api guide.

If variable is single level, then the product is "reanalysis-era5-single-levels"
and no pressure level field is required.  If variable is on a pressure level,
then the product is "reanalysis-era5-pressure-levels" and a pressure level
field is required.

For global data, no area field is required.  Otherwise, specify the required
area by latitude and longitude coordinates.

This code ouputs files in netcdf (.nc) format - easy to use with xarray for
array manipulation.

@author: robertrouse
"""

# Import cdsapi and create a Client instance
import cdsapi
import xarray as xr


def query(filename, product, variables, gridsquare, years, months,
                   days, times, pressure_levels='n/a'):
    '''
    Creates a standardised dataquery in dictionary format that can be passed
    to initialise the era5 class and subsequent download from the copernicus
    data store.

    Parameters
    ----------
    filename : String
        Filename stem to which the data will be saved.
    product : String
        ERA5 data product that is being accessed.  Refer to the CDS API for
        guidance on product names if further information is required.
    variables : String, List of strings
        Meteorologial variables to extract from the data product.
    gridsquare : String, List of strings
        Lat/Lon gridsquare over which to extract meteorological data.
    years : Integer, String, List of integers or strings
        Years at which to extract meteorological data.
    months : Integer, String, List of integers or strings
        Months at which to extract meteorological data.
    days : Integer, String, List of integers or strings
        Days at which to extract meteorological data.
    times : Integer, String, List of integers or strings
        Hours at which to extract meteorological data.
    pressure_levels : Integer, String, List of integers or strings, optional
        Pressure levels from which to extract varibles. The default is 'n/a'.

    Returns
    -------
    query : Dictionary
        Standardised data query format.

    '''
    query = {'file_stem':filename, 'product':product, 'variables':variables,
               'area':gridsquare, 'years':years, 'months':months, 'days':days,
               'times':times, 'pressure_levels':pressure_levels
               }
    return query


class era5():
    def __init__(self, query):
        '''
        Initialises the era5 data query class for accessing and downloading
        data via the CDS API.  Takes the standardised dictionary created
        using the query function from this library as input.

        Parameters
        ----------
        query : Dictionary
            Standardised data query, created using the query function from
            this library.

        Returns
        -------
        None.

        '''
        self.c = cdsapi.Client()
        self.query = query
        self.pressure_set = query['pressure_levels']

    def download(self):
        '''
        Initiates the download from the CDS, outputting data to the 
        target filename.

        Returns
        -------
        None.

        '''
        if self.pressure_set=='n/a':
            filename = str(self.query['file_stem']) + '.nc'
            self.c.retrieve(self.query['product'],
                            {"product_type":   "reanalysis",
                            "data_format":         "netcdf",
                            "variable":       self.query['variables'],
                            "area":           self.query['area'],
                            "year":           self.query['years'],
                            "month":          self.query['months'],
                            "day":            self.query['days'],
                            "time":           self.query['times']},
                            filename)
        else:
            for p in self.pressure_set:
                filename = str(self.query['file_stem']) + str(p) + 'hPa.nc'
                self.c.retrieve(self.query['product'],
                                {"product_type":   "reanalysis",
                                "data_format":         "netcdf",
                                "pressure_level": [p],
                                "variable":       self.query['variables'],
                                "area":           self.query['area'],
                                "year":           self.query['years'],
                                "month":          self.query['months'],
                                "day":            self.query['days'],
                                "time":           self.query['times']},
                                filename)


def aggregate_mean(in_file, out_file, time='24H'):
    '''
    Aggregates hourly array data, stored in a netcdf format, using xarray
    to a daily mean variable instead and outputs to a target file.
    Aggregates across all meteorological variables.

    Parameters
    ----------
    in_file : String
        Input hourly data file.  Expects netcdf format or similar.
    out_file : String
        Output daily data file.  Expects netcdf format or similar.
    time : String, optional
        Time step over which to apply the aggregation. The default is '24H'.

    Returns
    -------
    None.

    '''
    original = xr.open_dataset(in_file)
    cache = original.resample(time=time).mean('time')
    cache.to_netcdf(out_file)


def aggregate_max(in_file, out_file, time='24H'):
    '''
    Aggregates hourly array data, stored in a netcdf format, using xarray
    to a daily maximum variable instead and outputs to a target file.
    Aggregates across all meteorological variables.

    Parameters
    ----------
    in_file : String
        Input hourly data file.  Expects netcdf format or similar.
    out_file : String
        Output daily data file.  Expects netcdf format or similar.
    time : String, optional
        Time step over which to apply the aggregation. The default is '24H'.
    
    Returns
    -------
    None.

    '''
    original = xr.open_dataset(in_file)
    cache = original.resample(time=time).max('time')
    cache.to_netcdf(out_file)