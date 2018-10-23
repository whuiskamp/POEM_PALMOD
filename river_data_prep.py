from netCDF4 import Dataset
import numpy as np
import numpy.ma as ma
from landlab import RasterModelGrid
from landlab.components import FlowRouter, DepressionFinderAndRouter, SinkFiller
from landlab import BAD_INDEX_VALUE as XX
import matplotlib
import matplotlib.pyplot as plt
from landlab.plot.drainage_plot import drainage_plot
import sys
import math

# This script will prepare the input file land_lad2 requires for its river routing scheme.
# Data comes from the ICE-6G-C reconstruction and should have already been regridded to the
# land_lad2 grid resolution.
# Arguments:
# year 			 - The year for which you are creating the river network
# 				   (should be defined in years kbp, eg: 21 -> 0.5)
# river_rout_out - The new river routing file with updated tocell field that will be the output
# This script requires the landlab package (https://github.com/landlab/landlab/wiki).
# To run: Activate LGM anaconda environment 'source activate LGM'
# eg:	  python river_data_prep 21 river_data_LGM
# Willem Huiskamp, 2018

# Get external arguments

year = sys.argv[1]
river_rout_out = sys.argv[2]

# 1) prepare new tocell field for ice sheets
# Import re-gridded ice sheet topography

ice = Dataset(('/p/projects/climber3/huiskamp/POEM/work/LGM_data/ICE-6G-C/ICE-6G-C_LL2/I6_C.VM5a_LL2.',year,'.nc'),'r')
ice_topo = ice.variables['OROG_LL2'][:]; # [360,720]
ice_topo_f = np.flipud(ice_topo)
ice_mask = ice.variables['ICE_MASK_LL2'][:];
ice_mask_f = np.flipud(ice_mask)
lon = ice.variables['GRID_X'][:]
lat = ice.variables['GRID_Y'][:]
ice.close()

# Extend the field at the bottom and sides (one will contain no flow) to avoid hard boundaries.
# ie: The Earth is replicated 6 times here.
# Note that ICE-6G-C fields have a row of NaNs at the bottom and top of the field.
# Map looks like this:   _______ _______ _______
#						|_______|_______|_______|
#						|_______|_______|_______| <- This row is upside down.
#
extend_t = np.zeros([lat.shape[0]*2-2,lon.shape[0]*3]) # -2 to remove NaN line on bottom
extend_t[0:lat.shape[0]-1,0:lon.shape[0]] = ice_topo_f[0:lat.shape[0]-1,:] # top left
extend_t[0:lat.shape[0]-1,lon.shape[0]:lon.shape[0]*2] = ice_topo_f[0:lat.shape[0]-1,:] # top centre
extend_t[0:lat.shape[0]-1,lon.shape[0]*2:lon.shape[0]*3] = ice_topo_f[0:lat.shape[0]-1,:] # Top right 
extend_t[lat.shape[0]-1:lat.shape[0]*2-2,0:lon.shape[0]*3] = np.fliplr(np.flipud(extend_t[0:lat.shape[0]-1,0:lon.shape[0]*3])) # pad bottom

# Create raster grid for flow calculation and add data
fg = RasterModelGrid((extend_t.shape[0], extend_t.shape[1]), spacing=(1, 1))
_ = fg.add_field('node','topographic__elevation', extend_t)

fg.set_closed_boundaries_at_grid_edges(False, False, False, False)

# Calculate flow fields
fr = FlowRouter(fg)
fg = fr.route_flow()

# Preview the flow field with this plotting func.
# drainage_plot(fg, title='Grid 2 using FlowDirectorD8')

# Fill in Lakes/depressions
fg.at_node['flow__sink_flag'][fg.core_nodes].sum() # how many depressions do we have?
hf = SinkFiller(fg, apply_slope=True)
hf.run_one_step()
fr.run_one_step()
# drainage_plot(fg, title='Grid 2 using FlowDirectorD8')
# Output is a single vector
flow_rec = fg.at_node['flow__receiver_node']


# Convert to a 'tocell' field
# In land_lad2, directions are defined using the standard D8 method as follows
#
# [32, 64, 128]
# [16, 0,    1]
# [8,  4,    2]

tocell_tmp = np.zeros([flow_rec.shape[0]])
for i in range(flow_rec.shape[0]):
#	print('i= '+str(i))
	if flow_rec[i] == i: # if it flows to itself
		tocell_tmp[i] = 0
	elif flow_rec[i] == i+1: # to the east
		tocell_tmp[i] = 1
	elif flow_rec[i] == i+extend_t.shape[1]: # to the south
		tocell_tmp[i] = 4
	elif flow_rec[i] == i+extend_t.shape[1]+1: # to the south-east
		tocell_tmp[i] = 2
	elif flow_rec[i] == i-1: # to the west
		tocell_tmp[i] = 16
	elif flow_rec[i] == i+extend_t.shape[1]-1: # to the south-west
		tocell_tmp[i] = 8
	elif flow_rec[i] == i-extend_t.shape[1]: # to the north
		tocell_tmp[i] = 64
	elif flow_rec[i] == i-extend_t.shape[1]+1: # to the north-east
		tocell_tmp[i] = 128
	elif flow_rec[i] == i-extend_t.shape[1]-1: # to the north-west
		tocell_tmp[i] = 32
	else:
		print('Something has gone wrong at point ' + str(i))

tocell = np.reshape(tocell_tmp,(-1,extend_t.shape[1]))
tocell_c = np.zeros([lat.shape[0],lon.shape[0]])
tocell_c = tocell[0:lat.shape[0],lon.shape[0]:lon.shape[0]*2]

######### Create single Earth from tocell field #################

river = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/River_data/river_network_mrg_0.5deg_autodrain_3nov08.fill_coast_auto2.nc','r')
tocell_pi = river.variables['tocell'];
tocell_pi_f = np.flipud(tocell_pi)
tocell_LGM = np.zeros([lat.shape[0],lon.shape[0]])
tocell_LGM[2:300,:] = tocell_c[2:300,:]


######################## Update land mask ###########################

land_mask_f = np.zeros([lat.shape[0],lon.shape[0]])
land_mask_f[ice_topo_f>0] = 1; land_mask_f[359,:] = 1
# Alter your tocell field to eliminate ocean tiles
tocell_LGM[land_mask_f<1] = np.nan; tocell_LGM[0,:] = np.nan

for i in range(300,360):
	for j in range(720):
		if tocell_pi_f[i,j] >= 0:
			tocell_LGM[i,j] = tocell_pi_f[i,j] 


# Finally, outflow cells at the coast

# [32, 64, 128]
# [16, 0,    1]
# [8,  4,    2]

tocell_vec = tocell_LGM.flatten()
for i in range(tocell_vec.shape[0]-1440): # We can leave off the last two rows (this is just land anyway) - makes things easier.
	if tocell_vec[i] > 0:
		if tocell_vec[i] == 1 and np.isnan(tocell_vec[i+1]) == True:	
			tocell_vec[i+1] = 0
		if tocell_vec[i] == 16 and np.isnan(tocell_vec[i-1]) == True:	
			tocell_vec[i-1] = 0
		if tocell_vec[i] == 4 and np.isnan(tocell_vec[i+720]) == True:	
			tocell_vec[i+720] = 0
		if tocell_vec[i] == 64 and np.isnan(tocell_vec[i-720]) == True:
			tocell_vec[i-720] = 0
		if tocell_vec[i] == 2 and np.isnan(tocell_vec[i+720+1]) == True:	
			tocell_vec[i+720+1] = 0
		if tocell_vec[i] == 128 and np.isnan(tocell_vec[i-720+1]) == True:
			tocell_vec[i-720+1] = 0
		if tocell_vec[i] == 8 and np.isnan(tocell_vec[i+720-1]) == True:	
			tocell_vec[i+720-1] = 0
		if tocell_vec[i] == 32 and np.isnan(tocell_vec[i-720-1]) == True:
			tocell_vec[i-720-1] = 0

# Does it look OK?
fixed_test = np.reshape(tocell_vec,(-1,tocell_LGM.shape[1]))
# plt.imshow(fixed_test)
# plt.show()

######################## Re-update the damn land mask #########################
land_mask_f = np.zeros([lat.shape[0],lon.shape[0]])
land_mask_f[fixed_test>0] = 1

######################## Create new cell-area field ###########################
pi = math.pi
R = 6371000 # radius of the earth (m)
area = np.zeros([lat.shape[0],lon.shape[0]])
for i in range(lat.shape[0]-1):
	area[i,:] = (R**2)*abs(np.sin(np.deg2rad(lat[i]))-np.sin(np.deg2rad(lat[i+1])))*np.deg2rad(0.5)  # the lon resolution is half a degree
	area[359,:] = area[0,:]

cellarea = np.zeros([lat.shape[0],lon.shape[0]])
cellarea[land_mask_f>0] = area[land_mask_f>0]

######################## Output to NetCDF file ###########################
print('Writing NetCDF file for ',year,'ka')
id = Dataset(river_rout_out, 'w')
# id = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/River_data/test4.nc', 'w')
id.createDimension('lon', lon.shape[0])
id.createDimension('lat', lat.shape[0])
id.createVariable('lon', 'f8', ('lon'))
id.variables['lon'].units = 'degrees'
id.variables['lon'][:] = lon[:]
id.createVariable('lat', 'f8', ('lat'))
id.variables['lat'].units = 'degrees'
id.variables['lat'][:] = lat[:]
id.createVariable('tocell', 'f8', ('lat', 'lon'))
id.variables['tocell'].units = 'none'
id.variables['tocell'][:,:] = np.flipud(fixed_test)
id.createVariable('land_frac', 'f8', ('lat', 'lon'))
id.variables['land_frac'].units = 'none'
id.variables['land_frac'][:,:] = np.flipud(land_mask_f)
id.createVariable('cellarea', 'f8', ('lat', 'lon'))
id.variables['cellarea'].units = 'none'
id.variables['cellarea'][:,:] = np.flipud(cellarea)
# id.createVariable('x_flow', 'f8', ('lat', 'lon'))
# id.variables['x_flow'].units = 'none'
# id.variables['x_flow'][:,:] = np.fliplr(x_flow2)
# id.createVariable('y_flow', 'f8', ('lat', 'lon'))
# id.variables['y_flow'].units = 'none'
# id.variables['y_flow'][:,:] = np.fliplr(y_flow2)
id.close()

id = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/River_data/land_mask_LGM.nc', 'w')
id.createDimension('lon', lon.shape[0])
id.createDimension('lat', lat.shape[0])
id.createVariable('lon', 'f8', ('lon'))
id.variables['lon'].units = 'degrees'
id.variables['lon'][:] = lon[:]
id.createVariable('lat', 'f8', ('lat'))
id.variables['lat'].units = 'degrees'
id.variables['lat'][:] = lat[:]
id.createVariable('land_frac', 'f8', ('lat', 'lon'))
id.variables['land_frac'].units = 'none'
id.variables['land_frac'][:,:] = np.flipud(land_mask_f)
id.close()

# We need to regrid the land mask for input into the GFDL river_regrid tool.
os.system("pyferret -script land_mask_regrid") # This assumes you've already saved the land mask below
L_mask = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/land_mask_reg.nc','r')
mask = L_mask.variables['LAND_FRAC_R']
lon_L = L_mask.variables['GRID_X']
lat_L = L_mask.variables['GRID_Y']

id = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/River_data/land_mask_tile1.nc', 'w')
id.createDimension('nx', lon_L.shape[0])
id.createDimension('ny', lat_L.shape[0])
id.createVariable('nx', 'f8', ('nx'))
id.variables['nx'].units = 'degrees'
id.variables['nx'][:] = lon_L[:]
id.createVariable('ny', 'f8', ('ny'))
id.variables['ny'].units = 'degrees'
id.variables['ny'][:] = lat_L[:]
id.createVariable('mask', 'f8', ('ny', 'nx'))
id.variables['mask'].units = 'none'
id.variables['mask'][:,:] = mask[:,:]
id.close()






