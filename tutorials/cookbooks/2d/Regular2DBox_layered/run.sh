#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

. clean.sh

rm log.*
# foamListTimes -rm
runApplication blockMesh
runApplication setFields
runApplication $application
# paraFoam
# . extractPlumeT.sh