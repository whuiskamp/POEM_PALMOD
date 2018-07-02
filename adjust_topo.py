from netCDF4 import Dataset
import numpy as np 

# This script will update the bathymetry and land/sea mask in topog.nc
# and write out a new file for the appropriate time-slice.
# 

def adjust_topo(old_topo_in_path, topo_anomaly_path, new_topo_out)

# Read in data

old = Dataset(old_topo_in_path, 'r')
anom = Dataset(topo_anomaly_path, 'r')

old_t = old.variables['depth']; old.close()
delta_t = anom.variables['']; anom.close()
new_t = np.zeros(old_t.shape[0],old_t.shape[1])

# Apply change in topo.
new_t[:] = old_t[:] + delta_t[:]

# Adjust mask and enforce min depth of 30m

new_t[new_t<=0] = 0
new_t[0<new_t<30] = 30

# for i in range(1,new_t.shape[0]+1):
# 	for j in range(1,new_t.shape[1]+1):
# 		if delta_t(i,j) == 0:
# 		   new_t(i,j) == 0 


