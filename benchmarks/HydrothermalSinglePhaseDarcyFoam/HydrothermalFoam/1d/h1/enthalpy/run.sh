#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

# get total ExecutionTime
start_time=`date +%s`

./clean.sh
runApplication blockMesh
runApplication $application
# paraFoam

# get total ExecutionTime
end_time=`date +%s`
echo execution time was `expr $end_time - $start_time` s.