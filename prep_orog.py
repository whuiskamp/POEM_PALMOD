from netCDF4 import Dataset
import numpy as np 
import sys
import matplotlib
import matplotlib.pyplot as plt
import subprocess
import time

### This script will create a file similar to navy_topography.data.nc for the model,
### but with the correct land/sea mask and ice sheets for the time-slice you want.

year = sys.argv[1] # should be kyrBP

# Read in data
orog = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/ICE-6G-C/I6_C.VM5a_1deg.'+str(year)+'.nc','r')
ht = orog.variables['orog'][:]
lon = orog.variables['lon'][:]
lat = orog.variables['lat'][:]
orog.close()

# Convert degrees to radians (deg * pi/180)
lon_edge = np.arange(0,361,1)
lat_edge = np.arange(-90,91,1)

xdat = np.radians(lon_edge)
ydat = np.radians(lat_edge)
zdat = ht

# Write data to new file

id = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/ground_type/orog_'+str(year)+'.nc', 'w')
id.createDimension('x', 360)
id.createDimension('y', 180)
id.createDimension('x1',1)
id.createDimension('x2',361)
id.createDimension('x3',181)
id.createVariable('xdat', 'f8', ('x2'))
id.variables['xdat'].units = 'radians_east'
id.variables['xdat'].cartesian_axis = 'X'
id.variables['xdat'].long_name = 'longitude (radians)'
id.variables['xdat'][:] = xdat[:]
id.createVariable('ydat', 'f8', ('x3'))
id.variables['ydat'].units = 'radians_north'
id.variables['ydat'].cartesian_axis = 'Y'
id.variables['ydat'].long_name = 'latitude (radians)'
id.variables['ydat'][:] = ydat[:]
id.createVariable('zdat', 'f8', ('y','x'))
id.variables['zdat'].units = 'meters'
id.variables['zdat'].cartesian_axis = 'Z'
id.variables['zdat'].long_name = 'height above sea level'
id.variables['zdat'][:] = zdat[:]
id.createVariable('ipts', 'f8', ('x1'))
id.variables['ipts'].units = 'none'
id.variables['ipts'].long_name = 'number of lon cells'
id.variables['ipts'][:] = 360
id.createVariable('jpts', 'f8', ('x1'))
id.variables['jpts'].units = 'none'
id.variables['jpts'].long_name = 'number of lat cells'
id.variables['jpts'][:] = 180

id.description = "Replacement for orography file navy_topography.data.nc derived from orog field in file I6_C.VM5a_1deg."+str(year)+".nc"
id.history = "Created " + time.ctime(time.time())
id.source = "created using /p/projects/climber3/huiskamp/POEM/work/LGM_data/scripts/prep_orog.py"
id.close()