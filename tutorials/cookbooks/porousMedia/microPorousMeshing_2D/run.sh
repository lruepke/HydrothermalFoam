#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

./clean.sh
# 1. meshing
gmsh gmsh/TAG.geo -3 -o gmsh/TAG.msh -format msh22
# 2. convert mesh
gmshToFoam gmsh/TAG.msh
# 4. set permeability
runApplication setFields
# 5. run
runApplication $application
# 6. postprocessing
# ./postProcess.sh