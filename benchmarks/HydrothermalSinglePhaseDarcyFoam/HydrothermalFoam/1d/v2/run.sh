#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

./clean.sh

# gmshToFoam gmsh/mesh_1D_vertical.msh
# ./renameboundary.sh
runApplication blockMesh
runApplication $application
# paraFoam