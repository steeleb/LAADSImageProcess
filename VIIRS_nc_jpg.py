# import modules

import matplotlib.pyplot as plt
import netCDF4 as nc

#point to directory
dir = '/Users/steeleb/OneDrive - Colostate/Superior/images/LAADS_VIIRS_nc/'

#for now, work with one file
file = dir + 'VJ102IMG.A2018091.1942.021.2021023002114.nc'

#read in as netcdf; xarray will not recognize the dimensions
viirs = nc.Dataset(file)

#store the band group in it's own object
viirs_bands = viirs['observation_data']
viirs_bands['I01']

