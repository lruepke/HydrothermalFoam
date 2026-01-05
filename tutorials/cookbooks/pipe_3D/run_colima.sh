#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

./clean.sh
# change core number and library extension name on colima
./change_colima.sh

gmshToFoam gmsh/mesh.msh

runApplication setFields
runApplication decomposePar
runParallel $application
runApplication reconstructPar

# paraFoam 
