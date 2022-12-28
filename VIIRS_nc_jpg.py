# import modules
import os
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
from PIL import Image


#point to directory
dir = '/Users/steeleb/OneDrive - Colostate/Superior/images/LAADS_VIIRS_nc/'

#get a list of files here
files = os.listdir(dir)
#and look at the list to make sure it seems right
print(files)

#for now, work with one file
file = dir + files[4]

#read in as netcdf; xarray will not recognize the dimensions
viirs = nc.Dataset(file, 'r')

print(viirs)

#store the band group in it's own object
viirs_bands = viirs['observation_data']
#store the image geolocs in their own object
viirs_locs = viirs['scan_line_attributes']

#view names of the variables
print(viirs_bands.variables.keys())

#VIIRS natural rgb are M10, M7, M5 - grab their masked layers
v_natred = viirs_bands.variables['M10'][:]
v_natgreen = viirs_bands.variables['M07'][:]
v_natblue = viirs_bands.variables['M05'][:]
#apply the mask to the layer
v_natred = v_natred.filled(0)
v_natgreen = v_natgreen.filled(0)
v_natblue = v_natblue.filled(0)

#True color rgb is M5, M4, M3
v_truered = viirs_bands.variables['M05'][:]
v_truegreen = viirs_bands.variables['M04'][:]
v_trueblue = viirs_bands.variables['M03'][:]
#apply the mask to the layer
v_truered = v_truered.filled(0)
v_truegreen = v_truegreen.filled(0)
v_trueblue = v_trueblue.filled(0)

#composite into rgb
v_nat_rgb = np.dstack((v_natred, v_natgreen, v_natblue))
v_true_rgb = np.dstack((v_truered, v_truegreen, v_trueblue))
v_natimage = Image.fromarray(v_nat_rgb, 'RGB')
v_trueimage = Image.fromarray(v_true_rgb, 'RGB')

plt.imshow(v_natimage)
plt.show()

img = np.array(rgb_array, dtype=int).reshape((1, len(rgb_array), 3))
plt.imshow(img, extent=[0, 16000, 0, 1], aspect='auto')
plt.show()

v_natimage.save('viirs_nat.jpg')
v_trueimage.save('viirs_true.jpg')
