from netCDF4 import Dataset
import numpy as np 
from copy import deepcopy
import time

river = Dataset('/p/projects/climber3/huiskamp/POEM/work/ESM2M_coarse_test/tests/river_network.tile1.nc','r')
SUBA = river.variables['subA']
TOCELL1 = river.variables['tocell']
TRAVEL = river.variables['travel']
BASIN = river.variables['basin']
CELLAREA = river.variables['cellarea']
CELLLENGTH = river.variables['celllength']
LAND_FRAC = river.variables['land_frac']
lon = river.variables['grid_x']
lat = river.variables['grid_y']

oldriver = Dataset('/p/projects/climber3/huiskamp/POEM/work/ESM2M_coarse_test/INPUT/river_data.nc','r')
INTERNAL = oldriver.variables['internal']
LAKE_FRAC = oldriver.variables['lake_frac']
LDS = oldriver.variables['lake_depth_sill']
LT = oldriver.variables['lake_tau']
WB = oldriver.variables['WaterBod']
PW = oldriver.variables['PWetland']
CTN = oldriver.variables['connected_to_next']
WLA = oldriver.variables['whole_lake_area']
IGL = oldriver.variables['igageloc']
JGL = oldriver.variables['jgageloc']
BNG = oldriver.variables['bname_gage']
X = oldriver.variables['x']
Y = oldriver.variables['y']

# The river_regrid tool is not perfect, it results in several inland drainage cells, which we have to manually correct.
# Note that after doing this, all other fields based on tocell have to be re-calculated using cp_river_vars!!
# This section only for use on river_data_coarse.nc file that is produced by the regridding script.

TOCELL = deepcopy(TOCELL1[:,:])
# TOCELL[51,17] = 1 
# TOCELL[51,18] = 1
# TOCELL[52,15] = 1
# TOCELL[53,17] = 1
# TOCELL[53,18] = 1
# TOCELL[55,42] = 4
# TOCELL[56,15] = 16
# TOCELL[56,20] = 2
# TOCELL[58,20] = 2
# TOCELL[65,16] = 8
# TOCELL[70,112] = 64
# TOCELL[76,14] = 64
# TOCELL[77,9] = 32
# TOCELL[78,99] = 32
# TOCELL[57,21] = 4
# TOCELL[79,11] = 64
# TOCELL[79,35] = 64
# TOCELL[79,48] = 64
# TOCELL[79,83] = 64
# TOCELL[79,107] = 64
# TOCELL[82,133] = 1

id = Dataset('/p/projects/climber3/huiskamp/POEM/work/ESM2M_coarse_test/INPUT/river_data_landfix.nc', 'w')
id.createDimension('grid_x', lon.shape[0])
id.createDimension('grid_y', lat.shape[0])
id.createDimension('ngage',31)
id.createDimension('nchar',4)
id.description = "river data for coarse resolution config of ESM2M. Lake data has not been altered"
id.history = "Created " + time.ctime(time.time())
id.source = "created using /p/projects/climber3/huiskamp/POEM/work/ESM2M_coarse_test/river_regrid.py"

id.createVariable('grid_x', 'f8', ('grid_x'))
id.variables['grid_x'].units = 'degrees_east'
id.variables['grid_x'].cartesian_axis = 'X'
id.variables['grid_x'].long_name = 'T-cell longitude'
id.variables['grid_x'][:] = lon[:]
id.createVariable('grid_y', 'f8', ('grid_y'))
id.variables['grid_y'].units = 'degrees_north'
id.variables['grid_y'].cartesian_axis = 'Y'
id.variables['grid_y'].long_name = 'T-cell latitude'
id.variables['grid_y'][:] = lat[:]
id.createVariable('subA', 'f8', ('grid_y', 'grid_x'))
id.variables['subA'].units = 'm2'
id.variables['subA'].missing_value = -9999
id.variables['subA'].long_name = 'sub-basin area'
id.variables['subA'][:,:] = SUBA[:,:]
id.createVariable('tocell', 'f8', ('grid_y', 'grid_x'))
id.variables['tocell'].units = 'none'
id.variables['tocell'].missing_value = -9999
id.variables['tocell'].long_name = 'direction to downstream cell'
id.variables['tocell'][:,:] = TOCELL[:,:]
id.createVariable('travel', 'f8', ('grid_y', 'grid_x'))
id.variables['travel'].units = 'none'
id.variables['travel'].missing_value = -9999
id.variables['travel'].long_name = 'cells left to travel before reaching ocean'
id.variables['travel'][:,:] = TRAVEL[:,:]
id.createVariable('basin', 'f8', ('grid_y', 'grid_x'))
id.variables['basin'].units = 'none'
id.variables['basin'].missing_value = -9999
id.variables['basin'].long_name = 'river basin id'
id.variables['basin'][:,:] = BASIN[:,:]
id.createVariable('cellarea', 'f8', ('grid_y', 'grid_x'))
id.variables['cellarea'].units = 'm2'
id.variables['cellarea'].missing_value = -9999
id.variables['cellarea'].long_name = 'cell area'
id.variables['cellarea'][:,:] = CELLAREA[:,:]
id.createVariable('celllength', 'f8', ('grid_y', 'grid_x'))
id.variables['celllength'].units = 'm'
id.variables['celllength'].missing_value = -9999
id.variables['celllength'].long_name = 'cell length'
id.variables['celllength'][:,:] = CELLLENGTH[:,:]
id.createVariable('land_frac', 'f8', ('grid_y', 'grid_x'))
id.variables['land_frac'].units = 'none'
id.variables['land_frac'].missing_value = -9999
id.variables['land_frac'].long_name = 'land fraction'
id.variables['land_frac'][:,:] = LAND_FRAC[:,:]
id.createVariable('internal', 'f8', ('grid_y', 'grid_x'))
id.variables['internal'].units = 'none'
id.variables['internal'].missing_value = -9999
id.variables['internal'].long_name = 'internal drainage flag'
id.variables['internal'][:,:] = INTERNAL[:,:]
id.createVariable('x', 'f8', ('grid_y','grid_x'))
id.variables['x'].units = 'degrees_east'
id.variables['x'].long_name = 'Geographic longitude'
id.variables['x'][:,:] = X[:,:]
id.createVariable('y', 'f8', ('grid_y','grid_x'))
id.variables['y'].units = 'degrees_north'
id.variables['y'].long_name = 'Geographic latitude'
id.variables['y'][:,:] = Y[:,:]
id.createVariable('lake_frac', 'f8', ('grid_y', 'grid_x'))
id.variables['lake_frac'].units = 'none'
id.variables['lake_frac'].missing_value = -9999
id.variables['lake_frac'].long_name = 'lake fraction'
id.variables['lake_frac'][:,:] = LAKE_FRAC[:,:]
id.createVariable('lake_depth_sill', 'f8', ('grid_y', 'grid_x'))
id.variables['lake_depth_sill'].units = 'm'
id.variables['lake_depth_sill'].missing_value = -9999
id.variables['lake_depth_sill'].long_name = 'lake depth sill'
id.variables['lake_depth_sill'][:,:] = LDS[:,:]
id.createVariable('lake_tau', 'f8', ('grid_y', 'grid_x'))
id.variables['lake_tau'].units = 's'
id.variables['lake_tau'].missing_value = -9999
id.variables['lake_tau'].long_name = 'lake tau'
id.variables['lake_tau'][:,:] = LT[:,:]
id.createVariable('WaterBod', 'f8', ('grid_y', 'grid_x'))
id.variables['WaterBod'].units = 'none'
id.variables['WaterBod'].missing_value = -9999
id.variables['WaterBod'].long_name = 'Water Bodies'
id.variables['WaterBod'][:,:] = WB[:,:]
id.createVariable('PWetland', 'f8', ('grid_y', 'grid_x'))
id.variables['PWetland'].units = 'none'
id.variables['PWetland'].missing_value = -9999
id.variables['PWetland'].long_name = 'Permanent Wetlands'
id.variables['PWetland'][:,:] = PW[:,:]
id.createVariable('connected_to_next', 'f8', ('grid_y', 'grid_x'))
id.variables['connected_to_next'].units = 'none'
id.variables['connected_to_next'].missing_value = -9999
id.variables['connected_to_next'].long_name = 'lake connection flag'
id.variables['connected_to_next'][:,:] = CTN[:,:]
id.createVariable('whole_lake_area', 'f8', ('grid_y', 'grid_x'))
id.variables['whole_lake_area'].units = 'm2'
id.variables['whole_lake_area'].missing_value = -9999
id.variables['whole_lake_area'].long_name = 'total area of lake'
id.variables['whole_lake_area'][:,:] = WLA[:,:]
id.createVariable('igageloc', 'f8', ('ngage'))
id.variables['igageloc'].units = 'none'
id.variables['igageloc'].long_name = 'i index of gage cell'
id.variables['igageloc'][:] = IGL[:]
id.createVariable('jgageloc', 'f8', ('ngage'))
id.variables['jgageloc'].units = 'none'
id.variables['jgageloc'].long_name = 'j index of gage cell'
id.variables['jgageloc'][:] = JGL[:]
id.createVariable('bname_gage', 'S1', ('ngage', 'nchar'))
id.variables['bname_gage'].units = 'none'
id.variables['bname_gage'].long_name = 'basin name at gage cell'
id.variables['bname_gage'][:,:] = BNG[:,:]
id.close()






