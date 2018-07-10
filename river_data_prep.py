from netCDF4 import Dataset
import numpy as np
from landlab import RasterModelGrid
from landlab.components.flow_routing import FlowRouter
import matplotlib
import matplotlib.pyplot as plt
# import landlab plotting functionality
from landlab.plot.drainage_plot import drainage_plot

# This script will prepare the input file land_lad2 requires for its river routing scheme.
# Data used are the STN-30p river network (the default for CM2.5) which is then augmented 
# over North America and Eurasia to account for LGM ice sheets. This data comes from the 
# ICE-6G-C reconstruction.
# Data in:
# ice_sheet_topo - an orography field (elevation in m) from the ice sheet recon
#				   of your choice.
# river_rout_in  - An existing river routing field (specifically, tocell) you wish to update
# river_rout_out - The new river routing file with updated tocell field
# year 			 - The year for which you are creating the river network
# 				   (should be defined in years kbp, eg: 21 -> 0.5)
# This script requires the landlab package.
# Willem Huiskamp, 2018

def river_data_prep(ice_sheet_topo, river_rout_out, year)

# 1) prepare new tocell field for ice sheets
# Import re-gridded ice sheet topography

ice = Dataset('/p/projects/climber3/huiskamp/POEM/work/LGM_data/ICE-6G-C/ICE-6G-C_LL2/I6_C.VM5a_LL2.21.nc','r')
#ice = Dataset(ice_sheet_topo,'r')
ice_topo = ice.variables['OROG_LL2']; # [360,720]
ice_topo_f = np.flipud(ice_topo)

lon = ice.variables['GRID_X']
lat = ice.variables['GRID_Y']

# Extend the field at the bottom and sides by two (one will contain no flow) to avoid hard boundaries.
# Note that ICE-6G-C fields have a row of NaNs at the bottom and top of the field
# For our purposes, we can use this row in Antarctica for our extension.
extend_t = np.zeros([lat.shape[0]+1,lon.shape[0]+4])
extend_t[0:lat.shape[0],2:lon.shape[0]+2] = ice_topo_f[:,:] 
extend_t[0:lat.shape[0],0:1] = ice_topo_f[:,-2:-1]; extend_t[0:lat.shape[0],-2:-1] = ice_topo_f[:,0:1] # pad sides
extend_t[-2:-1,2:lon.shape[0]+2] = ice_topo_f[-3:-2,::-1] # pad bottom

# Create raster grid for flow calculation and add data
fg = RasterModelGrid((extend_t.shape[0], extend_t.shape[1]), spacing=(1, 1))
_ = fg.add_field('node','topographic__elevation', extend_t)

fg.set_closed_boundaries_at_grid_edges(False, False, False, False)

# Calculate flow fields (Should probably be using flow DIRECTOR instead?)
fr = FlowRouter(fg)
fg = fr.route_flow()

# Output is a single vector which can be reshaped with 
flow_rec = fg.at_node['flow__receiver_node']
test2 = np.reshape(flow_rec, (-1, extend_t.shape[1]))
test3 = fg.at_node['flow__link_to_receiver_node']
test4 = np.reshape(test3, (-1, extend_t.shape[1]))

drainage_plot(fg, title='Grid 2 using FlowDirectorD8')

# Convert to a 'tocell' field
# In land_lad2, directions are defined as follows
# [8,   4,    2]
# [16,  0,    1]
# [32,  64, 128]
tocell_tmp = np.zeros([flow_rec[0]])
for i in range(flow_rec.shape[0]):
#	print('i= '+str(i))
	if flow_rec[i] == i: # if it flows to itself
		tocell_tmp[i] = 0
	elif flow_rec[i] == i+1: # to the east
		tocell_tmp[i] = 1
	elif flow_rec[i] == i+extend_t.shape[1]: # to the south
		tocell_tmp[i] = 64
	elif flow_rec[i] == i+extend_t.shape[1]+1: # to the south-east
		tocell_tmp[i] = 128
	elif flow_rec[i] == i-1: # to the west
		tocell_tmp[i] = 16
	elif flow_rec[i] == i+extend_t.shape[1]-1: # to the south-west
		tocell_tmp[i] = 32
	elif flow_rec[i] == i-extend_t.shape[1]: # to the north
		tocell_tmp[i] = 4
	elif flow_rec[i] == i-extend_t.shape[1]+1: # to the north-east
		tocell_tmp[i] = 2
	elif flow_rec[i] == i-extend_t.shape[1]-1: # to the north-east
		tocell_tmp[i] = 8
	else:
		print('Something has gone wrong at point ' + str(i))

tocell = np.reshape(tocell_tmp,(-1,extend_t.shape[1]))
plt.imshow(tocell)
plt.show()




# ) Import the regridded ice extend fields, so we know which regions of the
#    flow map need to be updated.
# Import ice sheet mask and isolate these regions in our new flow field

# Update PI flow field with the new one



# ) Combine new fields with existing river network data 
# Import re-gridded STN-30p river network

river = Dataset(river_rout_in,'r')

# Output to NetCDF file
print 'Writing NetCDF file'
# id = Dataset(river_rout_out, 'w')
id = Dataset('test.nc', 'w')
id.createDimension('longitude', lon.shape[0])
id.createDimension('latitude', lat.shape[0])
id.createVariable('longitude', 'f8', ('longitude'))
id.variables['longitude'].units = 'degrees'
id.variables['longitude'] = lon
id.createVariable('latitude', 'f8', ('latitude'))
id.variables['latitude'].units = 'degrees'
id.variables['latitude'] = lat
#id.createVariable('tocell', 'f8', ('latitude', 'longitude'))
#id.variables['tocell'].units = 'none'
#id.variables['tocell'][:,:] = test2
id.createVariable('FRN', 'f8',('latitude','longitude'))
id.variables['FRN'].units = 'none'
id.variables['FRN'][:,:] = np.flipud(test2[:,1:721])
id.createVariable('FLRN', 'f8',('latitude','longitude'))
id.variables['FLRN'].units = 'none'
id.variables['FLRN'][:,:] = np.flipud(test4[:,1:721])
id.close()




