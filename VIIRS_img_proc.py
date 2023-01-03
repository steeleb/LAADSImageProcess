# THIS SCRIPT HEAVILY BORROWS FROM https://git.earthdata.nasa.gov/projects/LPDUR/repos/nasa_viirs_surfacereflectance/browse/VIIRS_SR_Tutorial.ipynb
# If you're running this in RStudio, be sure to run the pySetup.Rmd script in this dirctory
# otherwise, you will need to create an environment as described at the link above in your terminal before running this script

#import modules
import h5py, os
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal, gdal_array
import datetime as dt
import pandas as pd
from skimage import exposure

#set up workspace
#point to where your viirs images are stored and where you'd like the jpg to be stored
inDir = '/Users/steeleb/OneDrive - Colostate/Superior/images/LAADS_VIIRS_VPN09GA/'
outDir = '/Users/steeleb/OneDrive - Colostate/Superior/images/LAADS_VIIRS_jpeg/'

# for our image we want to relay the information about the image quality
# here, we grab the bits for M3,4,5 (see table 14:https://viirsland.gsfc.nasa.gov/PDF/VIIRS_Surf_Refl_UserGuide_v1.3.pdf)
QF5bits = 8 #bits
QF5vals = list(range(0,(2**QF5bits))) #vals
QF5good = [] #goodQF

for v in QF5vals:
  bitVal = format(QF5vals[v], 'b').zfill(QF5bits)
  if bitVal[1:4] == '000':
    QF5good.append(QF5vals[v])
    print('\n' + str(QF5vals[v]) + ' = ' + str(bitVal))

#and then where there is water
QF2bits = 8
QF2vals = list(range(0,(2**QF2bits)))
water = []

for v in QF2vals:
  bitVal = format(QF2vals[v], 'b').zfill(QF2bits)
  if bitVal[-3:] == '010':
    water.append(QF2vals[v])
    print('\n' + str(QF2vals[v]) + ' = ' + str(bitVal))


#create a function to open image and grab metadata
def openimg(f):
  inFile = f
  outFile = inFile.rsplit('.', 1)[0]

  #get acquisition date from file name
  yeardoy = inFile.split('.')[1][1:]
  date = dt.datetime.strptime(yeardoy, '%Y%j').strftime('%Y-%m-%d')
  
  #read in the EOS5 file using the `h5py` module
  f = h5py.File(os.path.join(inDir, inFile), 'r')
  return(f, outFile)
  
# function to get metadata
def getMetadata(f):  
  fileMetadata = [m.decode('utf-8') for m in f['HDFEOS INFORMATION']['StructMetadata.0'][()].split()][0:33]
  return(fileMetadata)

meta = getMetadata(img)

def getSDS(f):
  #grab the GRIDS directory
  grids = list(f['HDFEOS']['GRIDS'])
  grids
  
  #identify the objects in the EOS5 file
  #create an empty list
  h5objs = [] 
  #walk through the objects, and add them to the list
  f.visit(h5objs.append)
  
  #get the datsets by invoking the grids (here, we're basically cycling through every possible data path in the EOS5 object)
  all_datasets = [obj for grid in grids for obj in h5objs if isinstance(f[obj],h5py.Dataset) and grid in obj] 
  all_datasets
  return(all_datasets)
 
all_ds = getSDS(img)


#create a function to process the images
def procimg(f, outFile, all_datasets):
  #grab rgb layers
  r = f[[a for a in all_datasets if 'M5' in a][0]]
  g = f[[a for a in all_datasets if 'M4' in a][0]]
  b = f[[a for a in all_datasets if 'M3' in a][0]]
  
  #look at the attributes in these layers
  list(r.attrs)
  
  #let's get the scaling factor and fill value and store them as a variable; we know the scale and Fill are the same for all bands
  scaleFactor = r.attrs['Scale'][0]
  fillValue = r.attrs['_FillValue'][0]
  
  #apply scaleFactor to our bands
  r = r[()]*scaleFactor
  g = g[()]*scaleFactor
  b = b[()]*scaleFactor
  
  #create an RGB array using `np.dstack()` and set fill values to nan
  rgb = np.dstack((r, g, b))
  rgb[rgb == fillValue * scaleFactor] = 0
  
  #using the 2nd and 98th percentiles of each band of the image, we'll rescale
  p2, p98 = np.percentile(rgb, (2,98))
  rgbStretched = exposure.rescale_intensity(rgb, in_range = (p2, p98))
  #and then do a gamma correction
  rgbStretched = exposure.adjust_gamma(rgbStretched, 0.5)
  
  #and now to plot and save
  fig = plt.figure(figsize =(12,12))
  ax = plt.Axes(fig,[0,0,1,1])
  ax.set_axis_off()
  fig.add_axes(ax)
  ax.imshow(rgbStretched, interpolation='bilinear', alpha=0.9) 
  fig.savefig('{}{}_nc.jpg'.format(outDir, outFile))     
  plt.close(fig)
  return(print('Image jpgs completed for: ', outFile))

#function to grab QA bands of interest
def getqa(f, all_datasets):
  #grab Quality Filter 5, a stand in for relative image quality
  qf5 = f[[a for a in all_datasets if 'QF5' in a][0]][()] # Import QF5 SDS
  q_water = f[[a for a in all_datasets if 'QF2' in a][0]][()] #Import QF2
  return(qf5, q_water)

q5, qw = getqa(img, all_ds)

  
def getMStack(f, all_datasets):
  #grab rgb layers
  M1 = f[[a for a in all_datasets if '_M1_' in a][0]]
  M2 = f[[a for a in all_datasets if '_M2_' in a][0]]
  M3 = f[[a for a in all_datasets if '_M3_' in a][0]]
  M4 = f[[a for a in all_datasets if '_M4_' in a][0]]
  M5 = f[[a for a in all_datasets if '_M5_' in a][0]]
  M7 = f[[a for a in all_datasets if '_M7_' in a][0]]
  M8 = f[[a for a in all_datasets if '_M8_' in a][0]]
  
  #let's get the scaling factor and fill value and store them as a variable; we know the scale and Fill are the same for all bands
  scaleFactor =M1.attrs['Scale'][0]
  fillValue = M1.attrs['_FillValue'][0]
  
  #apply scaleFactor to our bands
  M1 = M1[()] * scaleFactor
  M2 = M2[()] * scaleFactor
  M3 = M3[()] * scaleFactor
  M4 = M4[()] * scaleFactor
  M5 = M5[()] * scaleFactor
  M7 = M7[()] * scaleFactor
  M8 = M8[()] * scaleFactor
  
  return(M1, M2, M3, M4, M5, M7, M8, fillValue)

#run for example
img_mstack = getMStack(img, all_ds)  

#function to mask for QA of interest
def maskimg(band, qf5, QF5good, q_water, water):
  g_mask = np.ma.MaskedArray(band, np.in1d(qf5, QF5good, invert = True))
  w_mask = np.ma.MaskedArray(g_mask, np.in1d(q_water, water, invert = True))
  return(w_mask)

##not running##
for s in range(len(img_mstack)-1):
  one_band = maskimg(img_mstack[s], q5, QF5good, qw, water)
  if s == 0:
    all_bands = one_band
  else:
    all_bands = np.ma.dstack((all_bands, one_band))
  return(all_bands)

#function to georeference the images
img, outFile = openimg(files[0])
meta = getMetadata(img)

params = {'M3':{'data':one_band[2], 'band':'M3'},
          'M4':{'data':one_band[3], 'band':'M4'},
          'M5':{'data':one_band[4], 'band':'M5'}}  


def georef(meta, fillValue, params):
  # get lat and long of upper left corner
  ulc = [i for i in meta if 'UpperLeftPointMtrs' in i][0]
  ulcLon = float(ulc.split('=(')[-1].split(',')[0])
  ulcLat = float(ulc.split('=(')[-1].replace(')', '').split(',')[1])
  
  #set spatial resolution (actual res, nominal is 1k)
  yRes, xRes = -926.6254330555555,  926.6254330555555 
  geoInfo = (ulcLon, xRes, 0, ulcLat, 0, yRes)        
  
  #define crs projection
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
  
  for p in params:
    try:
      data = params[p]['data']
      data[data.mask == True] = fillValue
    except: AttributeError
    outputName = os.path.normpath('test.tif')
    nRow, nCol = data.shape[0], data.shape[1]
    dataType = gdal_array.NumericTypeCodeToGDALTypeCode(data.dtype)
    driver = gdal.GetDriverByName('GTiff')
    outFile = driver.Create(outputName, nCol, nRow, 1, dataType)
    band = outFile.GetRasterBand(1)
    band.WriteArray(data)
    band.FlushCache
    band.SetNoDataValue(float(fillValue))
    outFile.SetGeoTransform(geoInfo)
    outFile.SetProjection(prj)
    outFile = None
    print('Processing: {}'.format(outputName))
    

georef(meta, img_mstack[-1], params)    
    
#get file names and iterate through them
files = os.listdir(inDir)
length = len(files)

for f in files:
  img, outFile = openimg(f)
  procimg(img, outFile)
  
  
