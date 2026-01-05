#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

porousName="Unknown"
stlpath="stl"
function show_helpinfo()
{
    printf "usage: ${0##*/} -p<porousName> -s<stlPath> [-h]\n"
    printf "%s\t%s\n" "-p" "Name of the porous media, e.g. model3D, which is saved in the stl path"
    printf "%s\t%s\n" "-s" "What is your stl path, e.g. stl"
    printf "%s\t%s\n" "-h" "Show help information."
    exit 0
}
# 使用getopts从命令行获取参数
while getopts "hp:s:" arg
do
 case $arg in
  # 拾取到-h选项，显示帮助信息后退出
  h)
   show_helpinfo;;
  p)
   porousName=$OPTARG;; 
  s)
   stlpath=$OPTARG;;
  ?) 
   printf "error: unknow argument\nuse -h option to see help information.\n"
   show_helpinfo
 esac
done
# Check input parameters
if [ ${porousName} == "Unknown" ]; then
 show_helpinfo
fi

locationInMesh=${stlpath}/${porousName}/locationInMesh.txt

function mesh()
{
    stlname=$1
    caseDir=$2
    currentPath=${PWD}
    cp ${stlpath}/${porousName}/blockMeshDict ${caseDir}/system 
    mkdir ${caseDir}/constant/triSurface
    cp ${stlpath}/${porousName}.stl ${caseDir}/constant/triSurface/porous.stl
    cp ${stlpath}/${porousName}/inlet.stl ${caseDir}/constant/triSurface
    cp ${stlpath}/${porousName}/outlet.stl ${caseDir}/constant/triSurface
    cd $caseDir
    # cp ${stlpath}/blockMeshDict.$stlname ${caseDir}/system/blockMeshDict 
    surfaceFeatureExtract
    blockMesh
    # parallel run
    runApplication decomposePar
    runParallel snappyHexMesh -overwrite -parallel
    runApplication reconstructParMesh -constant -mergeTol 1e-6

    cd $currentPath
}
function changeLocationInMesh()
{
    regionID=$1
    caseDir=$2
    # change locationInMesh
    # awk '{gsub(/locationInMesh \(-0.45 0.05  0\);/, "locationInMesh (832	102.333336	0.519290);"); print }' system/snappyHexMeshDict > ${caseDir}/system/snappyHexMeshDict 
    x=`awk -v id=${regionID} 'NR==id{print $1}' $locationInMesh`
    y=`awk -v id=${regionID} 'NR==id{print $2}' $locationInMesh`
    z=`awk -v id=${regionID} 'NR==id{print $3}' $locationInMesh`
    echo "locationInMesh: " $x $y $z
    awk -v x=$x -v y=$y -v z=$z '{gsub(/.*locationInMesh.*/, "    locationInMesh ("x" "y" "z");"); print }' system/snappyHexMeshDict.orig > ${caseDir}/system/snappyHexMeshDict 

}
# 1. mesh the main stl (the largest one)
regionID=1
caseDir=.
changeLocationInMesh $regionID $caseDir
mesh ${porousName} $caseDir

# # 2. generate additional mesh if there are more than one valid regions
# for (( regionID=2; regionID<4; regionID++ ))
# do
#     caseDir=./region${regionID}
#     rm -rf $caseDir
#     # clone from master case
#     foamCloneCase . $caseDir
#     # change locationInMesh
#     changeLocationInMesh $regionID $caseDir
#     # meshing
#     mesh ${porousName} $caseDir
#     # merge mesh
#     # mergeMeshes . $caseDir -overwrite
#     echo "================region $regionID done"
# done
# # sed -e 's/.*locationInMesh.*/    fault ${caseDir}/' system/snappyHexMeshDict > ${caseDir}/system/snappyHexMeshDict 
# # mesh ${porousName} $caseDir
# # mergeMeshes . $caseDir -overwrite
# # rm -rf $caseDir

transformPoints -scale '(1E-6 1E-6 1E-6)'