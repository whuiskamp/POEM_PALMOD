#!/bin/bash
## This script alters the INPUT restart files for MOM5 in order to 
## change boundary conditions such as topography/ land sea mask mid-way through a 
## simulation. Run this from the experiment directory, NOT the INPUT dir.
## This script uses: Requires the GFDL/MOM tools (POEM/src/tools) make_topog,
## make_coupler_mosaic, 
##
## Remeber to set checksum_required = .false. in fms_io_nml in your input.nml file
## as we will be editing fields in the restart and they will no longer match their 
## checksums.
##
## W. Huiskamp, 2018   huiskamp@pik-potsdam.de

## 1) Create a directory and copy the restart files there

for i in $(awk '/Current/{print $1}' RESTART/coupler.res); do mkdir restart_files_yr_$i; mv RESTART/* restart_files_yr_$i; done
 

## 2)  Use MOM tools to change topog and mosaics - this will later have to be integrated into a loop.
## The tool requires Topo to have an attribute specifying missing data, so we need to add this (following loop only needs to be done once)
cd ../LGM_data/ICE-6G-C
for i in *.nc* ; do \
    ncatted -a missing_value\,Topo\,c\,f\,-99999 $i ; \
    ## ncflint -w -1,0.0 I6_C.VM5a_10min.21.nc I6_C.VM5a_10min.21.nc test_2.nc  ## this should work, but nco won't run for some reason. Meant to x all variables by -1.
done

## The below script will work now, and don't bother adding in other flags - the tool is garbage and doesn't even read them in.
## Try fregrid instead - maybe won't lose as many islands/ continents that way.
../../../src/tools/make_topog/make_topog \
        --mosaic ocean_mosaic.nc \
        --topog_type realistic \
        --topog_file /p/projects/climber3/huiskamp/POEM/work/LGM_data/ICE-6G-C/I6_C.VM5a_10min.21.nc \
        --topog_field Topo \
        --output topog_21k.nc \
        --fill_shallow \
        --bottom_depth 5500 \
        --vgrid_file ocean_vgrid.nc \
        --scale_factor -1 \
        --num_filter_pass 2 \
        --kmt_min 7 \
        --fill_first_row \
        --filter_topog

## We need to create a grid + mosaic file so that we can re-grid fields for the model. This is probably not nessecary actually...

../../../src/tools/make_hgrid/make_hgrid \
  --grid_type regular_lonlat_grid \
  --nxbnd 2 --nybnd 2 --xbnd -0.08\,359.9 --ybnd -90\,90 \
  --nlon 4320 --nlat 2160 \
  --verbose \
  --grid_name test_grid
  
../../../src/tools/make_solo_mosaic/make_solo_mosaic \
  --num_tiles 1 --dir ./ --mosaic_name ICE-6G_mosaic \
  --tile_file test_grid.nc  --periody 1
  
## Lets test it with the topo file ...




## 3) Change cross-land mixing params. in field table

## 4) 