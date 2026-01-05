#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

. clean.sh

# generate mesh using gmsh
gmsh gmsh/box.geo -3 -o gmsh/box.msh -format msh22
# convert gmsh to OpenFOAM format
gmshToFoam gmsh/box.msh
# run solver in parallel
runApplication decomposePar
runParallel $application
runApplication reconstructPar
