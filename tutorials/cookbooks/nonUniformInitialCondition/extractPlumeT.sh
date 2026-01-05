
# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application=`getApplication`

path_plumeT=postProcessing/plumeTemperature
mkdir -p $path_plumeT
awk '{if($0~"Plume Temperature: ") print $3, $4}' log.$application >$path_plumeT/plumtTemperature.txt