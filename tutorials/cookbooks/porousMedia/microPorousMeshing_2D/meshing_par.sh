# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions


# 1 cp stl to constant/triSurface
mkdir constant/triSurface
cp stl/image_pores.stl constant/triSurface/pores.stl

# 2. 
surfaceFeatureExtract
# 3. 
blockMesh
# parallel run
runApplication decomposePar
runParallel snappyHexMesh -parallel -overwrite
runApplication reconstructParMesh -constant -mergeTol 1e-6
rm -rf processor*
# snappyHexMesh

# extrude to generate 2D mesh
extrudeMesh
