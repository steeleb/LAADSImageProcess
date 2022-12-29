# Purpose: convert VIIRS L2 hdf to jpg
library(tidyverse)
library(stars)
library(terra)

#point to directory
imgdir = '/Users/steeleb/OneDrive - Colostate/Superior/images/LAADS_VIIRS_VPN09GA/'
dumpdir = '/Users/steeleb/OneDrive - Colostate/Superior/images/LAADS_VIIRS_jpeg'

#get a list of files here
img_files = list.files(imgdir, pattern = '.h5')

#get the date and time from these to match with geo dir
datetimelist = substr(img_files, 10, 16)

### play with a single file ----
file = img_files[1]

# STARS -----
#save subdatasets as an object
sd = gdal_subdatasets(file.path(imgdir, file))

#grab one of the i bands
I1=read_stars(sd[[24]])
I2=read_stars(sd[[25]])
I3=read_stars(sd[[26]])

M1=read_stars(sd[[7]])
M2=read_stars(sd[[8]])
M3=read_stars(sd[[9]])
M4=read_stars(sd[[10]])
M5=read_stars(sd[[11]])
M7=read_stars(sd[[12]])
M8=read_stars(sd[[13]])
M10=read_stars(sd[[5]])
M11=read_stars(sd[[6]])


