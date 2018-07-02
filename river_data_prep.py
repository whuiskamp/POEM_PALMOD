from netCDF4 import Dataset
import numpy as np
from landlab import RasterModelGrid
from landlab.components.flow_routing import FlowRouter

# This script will prepare the input file land_lad2 requires for its river routing scheme.
# Data used are the STN-30p river network (the default for CM2.5) which is then augmented 
# over North America and Eurasia to account for LGM ice sheets. This data comes from the 
# ICE-6G-C reconstruction.
# This script requires the landlab package.
# Willem Huiskamp, 2018

def river_data_prep(ice_sheet_topo, river_rout_in, river_rout_out, year)

# The script requires the year for which you are creating the river network
# This should be defined in years kbp (ie: 21 -> 0.5)

# 1) prepare new tocell field for ice sheets
# Import re-gridded ice sheet topography
### TO DO ### double the field at the bottom and sides to avoid hard boundaries.

ice = Dataset(ice_sheet_topo,'r')
ice_topo = ice.variables['orog']; old.close()

grid = RasterModelGrid((ice_topo.shape[0], ice_topo.shape[1]), spacing=(1, 1))
_ = mg.add_field('node','topographic__elevation', ice_topo)

mg.set_closed_boundaries_at_grid_edges(True, True, True, True)













# 2) Combine new fields with existing river network data 
# Import re-gridded STN-30p river network

river = Dataset(river_rout_in,'r')






