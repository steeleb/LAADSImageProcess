# Purpose: convert VIIRS L2 hdf to jpg
library(tidyverse)
library(stars)
library(jpeg)

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

#grab the i bands
I1=read_stars(sd[[24]])
max(I1$SurfReflect_I1_1)
I1 = I1/max(I1$SurfReflect_I1_1)

I2=read_stars(sd[[25]])
max(I2$SurfReflect_I2_1)
I2 = I2/max(I12SurfReflect_I2_1)

I3=read_stars(sd[[26]])
max(I3$SurfReflect_I3_1)
I3 = I3/10000

#grab the M bands
M1=read_stars(sd[[7]])
max(M1$SurfReflect_M1_1)
M1 = M1/max(M1$SurfReflect_M1_1)

M2=read_stars(sd[[8]])
M2= M2/max(M2$SurfReflect_M2_1)

M3=read_stars(sd[[9]])
M3 = M3/max(M3$SurfReflect_M3_1)

M4=read_stars(sd[[10]])
M4 = M4/max(M4$SurfReflect_M4_1)

M5=read_stars(sd[[11]])
M5 = M5/max(M5$SurfReflect_M5_1)

M7=read_stars(sd[[12]])
M1 = M1/max(M1$SurfReflect_M1_1)

M8=read_stars(sd[[13]])
M1 = M1/max(M1$SurfReflect_M1_1)

M10=read_stars(sd[[5]])
M10 = M10/max(M1$SurfReflect_M10_1)

M11=read_stars(sd[[6]])
M11 = M11/max(M11$SurfReflect_M11_1)

#create rgb images
# true color = M5, M4, M3
tc_rgb = array(c(M5$SurfReflect_M5_1, M4$SurfReflect_M4_1, M3$SurfReflect_M3_1),
               dim = c(nrow(M5$SurfReflect_M5_1), ncol(M5$SurfReflect_M5_1), 3))

#natural color = M10, M7, M5
nc_rgb = array(c(M10$SurfReflect_M10_1, M7$SurfReflect_M7_1, M5$SurfReflect_M5_1),
               dim = c(nrow(M10$SurfReflect_M10_1), ncol(M10$SurfReflect_M10_1), 3))

# save jpegs
writename = paste0(datetimelist[1], '_v', Sys.Date(), '.jpg')

writeJPEG(tc_rgb, file.path(dumpdir, paste0('tc_', writename)), quality =1)
writeJPEG(nc_rgb, file.path(dumpdir, paste0('nc_', writename)), quality =1)

