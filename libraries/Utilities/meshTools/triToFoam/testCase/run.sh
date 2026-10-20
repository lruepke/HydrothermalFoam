#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

. clean.sh

# generate mesh using Triangle
# triangle  -pQIq20Aane Triangle/box
# convert gmsh to OpenFOAM format
triToFoam Triangle/box
# run solver
runApplication $application
