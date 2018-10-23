from netCDF4 import Dataset
import numpy as np 
import sys
import matplotlib
import matplotlib.pyplot as plt


# This script will update the bathymetry and land/sea mask in topog.nc
# and write out a new file for the appropriate time-slice.
 
year = sys.argv[1] # should be kyrBP

# Read in data

topo = Dataset('tmp_topo.nc', 'r')
depth = topo.variables['TMP']; topo.close()

# Apply change in topo. Only lakes remain to be filled
# This section only applies to 21kyrBP
depth[64,95] = np.nan
depth[74,112:114] = np.nan
depth[75,114] = np.nan
depth[77,113:115] = np.nan
depth[78,112] = np.nan

# Adjust mask and enforce min depth of 30m and change land vals back to 0

mask = np.zeros(depth.shape) 
mask[depth<=0]=1
depth[mask==1]=0

depth[np.where((depth > 0) & (depth < 30))] = 30

id = Dataset('topog_final.nc', 'w')
id.createDimension('longitude', 120)
id.createDimension('latitude', 80)
id.createVariable('depth', 'f8', ('latitude', 'longitude'))
id.variables['depth'].units = 'm'
id.variables['depth'][:,:] = depth
id.close()

