#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# 1. Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions
# 2. get solver name
application=`getApplication`
# 3. clean case if necessary
./clean.sh
# 4. generate mesh file using gmsh command
gmsh gmsh/mesh.geo -3 -o gmsh/mesh.msh -format msh22
# 5. convert gmsh to OpenFOAM format
gmshToFoam gmsh/mesh.msh
# 6. set empty pathces for 2D case
changeDictionary
# 7. set fields
runApplication setFields

# 8.1 run a case using single thread
runApplication $application

# 8.2 or run a case in parallel
# runApplication decomposePar
# runParallel $application
# runApplication reconstructPar