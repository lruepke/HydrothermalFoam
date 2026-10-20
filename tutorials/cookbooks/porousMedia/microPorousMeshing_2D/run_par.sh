#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

./clean.sh
# change parallel processor number
awk '{gsub(/numberOfSubdomains 4;/, "numberOfSubdomains 64;"); print }' system/decomposeParDict.orig > system/decomposeParDict 

# 1. meshing
./meshing_par.sh
# 4. set permeability
runApplication setFields
# 5. run
# runApplication $application
rm log.*
runApplication decomposePar
runParallel $application
runApplication reconstructPar
rm -rf processor*
# 6. postprocessing
# ./postProcess.sh