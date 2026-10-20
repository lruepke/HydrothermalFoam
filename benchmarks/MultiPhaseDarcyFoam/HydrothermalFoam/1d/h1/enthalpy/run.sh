#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

./clean.sh
runApplication blockMesh

# sequential
runApplication $application
# # parallel
# runApplication decomposePar
# runParallel $application
# runApplication reconstructPar

# paraFoam

tail log.$application