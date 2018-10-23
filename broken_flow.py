## This script is designed to read in a standard D8 flow field and determine if there are infinite
## loops in the flow (either cells exchanging back and forth, or circular rivers).

from netCDF4 import Dataset
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

def broken_flow(input_file)

data = Dataset(input_file,'r')
tocell1 = data.variables['tocell'];
tocell = np.flipud(deepcopy(tocell1[:,:]));
flow = tocell.flatten()

# First, create a vector of destination flow cells for each cell.

dest_cell = np.zeros([flow.shape[0]])
x_flow = np.zeros([flow.shape[0]])
y_flow = np.zeros([flow.shape[0]])
for i in range(flow.shape[0]):
	if flow[i] == 0: # if it flows to itself
		dest_cell[i] = i
		x_flow[i] = 0
		y_flow[i] = 0
	elif flow[i] == 1:
		dest_cell[i] = i+1 # to the east
		x_flow[i] = 1
		y_flow[i] = 0
	elif flow[i] == 4:
		dest_cell[i] = i+tocell.shape[1] # to the south
		x_flow[i] = 0
		y_flow[i] = -1
	elif flow[i] == 2:
		dest_cell[i] = i+tocell.shape[1]+1 # to the south-east
		x_flow[i] = 1
		y_flow[i] = -1
	elif flow[i] == 16:
		dest_cell[i] = i-1 # to the west 
		x_flow[i] = -1
		y_flow[i] = 0		
	elif flow[i] == 8:
		dest_cell[i] = i+tocell.shape[1]-1 # to the south-west 
		x_flow[i] = -1
		y_flow[i] = -1		
	elif flow[i] == 64:
		dest_cell[i] = i-tocell.shape[1] # to the north 
		x_flow[i] = 0
		y_flow[i] = 1		
	elif flow[i] == 128:
		dest_cell[i] = i-tocell.shape[1]+1 # to the north-east
		x_flow[i] = 1
		y_flow[i] = 1	
	elif flow[i] == 32:
		dest_cell[i] = i-tocell.shape[1]-1 # to the north-west 
		x_flow[i] = -1
		y_flow[i] = 1

# # What does our flow field look like?
# x_flow2 = np.reshape(np.flipud(x_flow),(-1,tocell.shape[1]))
# y_flow2 = np.reshape(np.flipud(y_flow),(-1,tocell.shape[1]))

# plt.quiver(x_flow2,y_flow2, scale_units='xy')
# plt.show()	

dest_cell[np.isnan(dest_cell)] = 0
loops_pair = np.zeros([flow.shape[0]])
loops_inf = np.zeros([flow.shape[0]])

###############	Legend ############
# cc = current cell
# nc = next cell
# pc = previous cell
# cc_f = flow dir. of current cell

for i in range(flow.shape[0]):
	cc_f = int(dest_cell[i]) # path from current cell to the next cell
	path_len = 0
	cc = i
	pc = -1 # initialise an impossible number
	cont = flow[i]
	while (cont > 0): 
		nc = cc_f # cell to which the current cell flows (cell a(i) -> b(next_cell))
		path_len += 1 # If flow continues, its path length increases
		if nc == pc and path_len > 1000: # Kill loop if two cells flow to each other
			# print('Two cells flowing into each other at i='+str(i), 'pathlen='+str(path_len))
			loops_pair[cc] = 1
			break
		elif path_len > 1000: # Kill loop if there's an endless river (not the Pink Floyd kind)
			# print('infinite flow at i='+str(i), 'pathlen='+str(path_len))
			loops_inf[cc] = 1
			break
		cc_f = int(dest_cell[nc]) # Update flow path to be the cell that b flows to
		pc = cc # The previous cell will be what is now the current cell
		cc = nc # The current cell will be what was the next cell 
		cont = flow[cc] # To see if the river has ended, we see if the next cell is ocean (does cont = 0?)
		# print(cont)
	# print(i)

###### see what's going in in the flow fields #########
loops_array = np.flipud(np.reshape(loops_inf,(-1,tocell.shape[1])))
loops_array2 = np.flipud(np.reshape(loops_pair,(-1,tocell.shape[1])))
for i in range(loops_array.shape[1]):
	for j in range(loops_array.shape[0]):
		if loops_array[j,i] == 1 or loops_array2[j,i] == 1 :
			print('Problem at cell i='+str(i+1),',', 'j='+str(j+1))

dest_array = np.flipud(np.reshape(dest_cell,(-1,tocell.shape[1])))
flow_array = np.flipud(np.reshape(dest_cell,(-1,tocell.shape[1])))

# broken_flow = loops*flow
# flow_test = np.reshape(broken_flow,(-1,tocell.shape[1]))
# plt.imshow(flow_test)
# plt.show()