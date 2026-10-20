# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

porousName="Unknown"
stlpath="stl"
function show_helpinfo()
{
    printf "usage: ${0##*/} -p<porousName> -s<stlPath> [-h]\n"
    printf "%s\t%s\n" "-p" "Name of the porous media, e.g. model2D, which is saved in the stl path"
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

# foamCleanTutorials

function mesh()
{
    stlname=$1
    caseDir=$2
    currentPath=${PWD}
    cp ${stlpath}/${porousName}/blockMeshDict ${caseDir}/system 
    cp ${stlpath}/${porousName}/walls.stl ${caseDir}/constant/triSurface/porous.stl
    cp ${stlpath}/${porousName}/inlet.stl ${caseDir}/constant/triSurface
    cp ${stlpath}/${porousName}/outlet.stl ${caseDir}/constant/triSurface
    cp ${stlpath}/${porousName}/top.stl ${caseDir}/constant/triSurface
    cp ${stlpath}/${porousName}/bottom.stl ${caseDir}/constant/triSurface
    cp ${stlpath}/${porousName}/front.stl ${caseDir}/constant/triSurface
    cp ${stlpath}/${porousName}/back.stl ${caseDir}/constant/triSurface
    cd $caseDir
    cp ${stlpath}/blockMeshDict.$stlname ${caseDir}/system/blockMeshDict 
    surfaceFeatureExtract
    blockMesh
    # parallel run
    runApplication decomposePar
    runParallel snappyHexMesh -overwrite -parallel
    runApplication reconstructParMesh -constant -mergeTol 1e-6
    rm -rf processor*
    # make 2D mesh
    extrudeMesh
    touch mesh.foam
    cd $currentPath
}
function changeLocationInMesh()
{
    regionID=$1
    caseDir=$2
    # change locationInMesh
    x=`awk -v id=${regionID} 'NR==id{print $1}' $locationInMesh`
    y=`awk -v id=${regionID} 'NR==id{print $2}' $locationInMesh`
    z=`awk -v id=${regionID} 'NR==id{print $3}' $locationInMesh`
    echo "locationInMesh: " $x $y $z
    awk -v x=$x -v y=$y -v z=$z '{gsub(/.*locationInMesh.*/, "    locationInMesh ("x" "y" "z");"); print }' system/snappyHexMeshDict.orig > ${caseDir}/system/snappyHexMeshDict 

}
# 1. master mesh
regionID=1
caseDir=.
changeLocationInMesh $regionID $caseDir
mesh ${porousName} $caseDir

# # 2. generate additional mesh
# # get number of valid regions
# num_regions=`wc -l $locationInMesh | awk '{print $1}'`
# for (( regionID=2; regionID<=$num_regions; regionID++ ))
# do
#     caseDir=./region${regionID}
#     rm -rf $caseDir
#     # clone from master case
#     foamCloneCase . $caseDir
#     change locationInMesh
#     changeLocationInMesh $regionID $caseDir
#     # meshing
#     mesh ${porousName} $caseDir
#     # merge mesh
#     mergeMeshes . $caseDir -overwrite
#     echo "================region $regionID done"
#     rm -rf $caseDir
# done

# checkmesh
checkMesh -allGeometry -allTopology

# scaling
transformPoints -scale '(1E-6 1E-6 1E-6)'