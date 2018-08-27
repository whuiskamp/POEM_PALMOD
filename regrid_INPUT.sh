#!/bin/bash
## This script uses the GFDL tool fregrid to regrid input files from one resolution/ model configuration to another.
## $1 = input mosaic, $2 = input file, $3 = output mosaic, $4 = input dir., $5 = output dir.

/p/projects/climber3/huiskamp/POEM/src/tools/fregrid/fregrid --input_mosaic $1 --input_file $2 --output_mosaic $3 --input_dir $4 --output_dir $5

