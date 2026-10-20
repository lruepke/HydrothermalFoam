#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

./clean.sh
# cp system/controlDict.orig system/controlDict
gmsh gmsh/mesh.geo -3 -o gmsh/mesh.msh -format msh22
gmshToFoam gmsh/mesh.msh
runApplication setFields
runApplication $application
# runApplication decomposePar
# runParallel $application
# runApplication reconstructPar

# paraFoam 