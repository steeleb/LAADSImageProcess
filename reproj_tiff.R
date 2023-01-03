library(stars)
library(tidyverse)

tif = 'test.tif'
test = stars::read_stars(tif)
plot(test)

prj = 'PROJCS["unnamed",\
GEOGCS["Unknown datum based upon the custom spheroid", \
DATUM["Not specified (based on custom spheroid)", \
SPHEROID["Custom spheroid",6371007.181,0]], \
PRIMEM["Greenwich",0],\
UNIT["degree",0.0174532925199433]],\
PROJECTION["Sinusoidal"], \
PARAMETER["longitude_of_center",0], \
PARAMETER["false_easting",0], \
PARAMETER["false_northing",0], \
UNIT["Meter",1]]'

test2 = st_transform_proj(test, prj)
plot(test2)

test3 = st_transform(test, crs = st_crs(4326))
plot(test3)

print(prj)
