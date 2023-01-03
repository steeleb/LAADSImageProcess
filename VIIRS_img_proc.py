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


#create a function to process the images
def procimg(f, outFile):
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
  fig = plt.figure(figsize =(10,10))
  ax = plt.Axes(fig,[0,0,1,1])
  ax.set_axis_off()
  fig.add_axes(ax)
  ax.imshow(rgbStretched, interpolation='bilinear', alpha=0.9) 
  fig.savefig('{}{}_nc.png'.format(outDir, outFile))     
  plt.close(fig)
  return(print('Image processing completed for :', outFile))


#get file names and iterate through them
files = os.listdir(inDir)
length = len(files)

for f in files:
  img, outFile = openimg(f)
  procimg(img, outFile)
  

