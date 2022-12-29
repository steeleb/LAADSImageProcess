library(ncdf4)
library(stars)
library(jpeg)
library(tidyverse)

#point to directory
banddir = '/Users/steeleb/OneDrive - Colostate/Superior/images/LAADS_VIIRS_band/'
geodir = '/Users/steeleb/OneDrive - Colostate/Superior/images/LAADS_VIIRS_geo/'
dumpdir = '/Users/steeleb/OneDrive - Colostate/Superior/images/LAADS_VIIRS_jpeg'

#get a list of files here
band_files = list.files(banddir, pattern = '.nc')

#get the date and time from these to match with geo dir
datetimelist = substr(band_files, 11, 22)

#get the list of geo files
geo_files = list.files(geodir, pattern = '.nc')
#only list the ones that match
geo_files = geo_files[substr(geo_files, 11, 22)==datetimelist]


#############################
## grab band and geo files and metadata for file naming
date = datetimelist[1]

#for now, work with one file
bandfile = file.path(banddir, band_files[grepl(datetimelist[1], band_files)])
geofile = file.path(geodir, geo_files[grepl(datetimelist[1], geo_files)])

#read in as netcdf; neither xarray nor stars will recognize the dimensions
vi_band = nc_open(bandfile)
vi_geo = nc_open(geofile)

#get coordinates from global attributes of geo file
latitude <- ncvar_get(vi_geo, 'geolocation_data/latitude')
longitude <- ncvar_get(vi_geo, 'geolocation_data/longitude')

#get short product name from global attributes of band data
name <- ncatt_get(vi_band, 0)$ShortName

#store each band as its own array
tc_red = ncvar_get(vi_band, 'observation_data/M05')
tc_red[tc_red >1] <- NA_real_
tc_green = ncvar_get(vi_band, 'observation_data/M04')
tc_green[tc_green >1] <- NA_real_
tc_blue = ncvar_get(vi_band, 'observation_data/M03')
tc_blue[tc_blue >1] <- NA_real_

# tc_rgb = rgb(tc_red, tc_green, tc_blue)
# dim(tc_rgb) <- dim(tc_red)
# grid::grid.raster(tc_rgb)

nc_red = ncvar_get(vi_band, 'observation_data/M10')
nc_green = ncvar_get(vi_band, 'observation_data/M07')
nc_blue = ncvar_get(vi_band, 'observation_data/M05')

tc_rgb = array(c(tc_red, tc_green, tc_blue), 
               dim = c(nrow(tc_red), ncol(tc_red), 3))
nc_rgb = array(c(nc_red, nc_green, nc_blue), 
               dim = c(nrow(nc_red), ncol(nc_red), 3))

## save jpegs
writename = paste0(date, '_', name, '_v', Sys.Date(), '.jpg')

writeJPEG(tc_rgb, file.path(dumpdir, paste0('tc_', writename)), quality =1)
writeJPEG(nc_rgb, file.path(dumpdir, paste0('nc_', writename)), quality =1)

nc_close(viirs)
