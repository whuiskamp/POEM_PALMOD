from netCDF4 import Dataset
import numpy as np 
import sys
import matplotlib
import matplotlib.pyplot as plt
import subprocess
import time

# This script will update the land ice extent for a time-slice in ground_type.nc
# This assumes the model configuration is using land_lad2.
# and write out a new file for the appropriate time-slice.
 
year = sys.argv[1] # should be kyrBP

# Backup your ground_type file

subprocess.call(['cp', '/p/projects/climber3/huiskamp/POEM/exp/ESM2M_coarse/INPUT/ground_type.nc', \
 '/p/projects/climber3/huiskamp/POEM/work/LGM_data/ground_type/ground_type_'+str(year)+'.nc'])

# Read in data
grnd = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/ground_type/ground_type_'+str(year)+'.nc', 'a')
ice = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/ground_type/I6_C_regrid.'+str(year)+'.nc')

frac = grnd.variables['frac'][:]
new_ice = ice.variables['ICE_MASK_LL2'][:]; ice.close()

grnd.variables['frac'][8,:,:] = new_ice
grnd.description = "Ice sheet data (k=9) updated for "+str(year)+"kyrBP"
grnd.history = "Created " + time.ctime(time.time())
grnd.source = "created using /p/projects/climber3/huiskamp/POEM/work/LGM_data/scripts/update_ice_sheets.py"
grnd.close()
