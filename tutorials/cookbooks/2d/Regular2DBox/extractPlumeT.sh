
path_plumeT=postProcessing/plumeTemperature
mkdir -p $path_plumeT
awk '{if($0~"Plume Temperature: ") print $3, $4}' log.HTFoam >$path_plumeT/plumtTemperature.txt