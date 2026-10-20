awk -v RS="\0" -v ORS="" '{ gsub(/(frontAndBack)\n    {\n        type            patch/, "frontAndBack\n    {\n        type            empty"); print }' constant/polyMesh/boundary > tmp  
mv tmp constant/polyMesh/boundary

awk -v RS="\0" -v ORS="" '{ gsub(/(right)\n    {\n        type            patch/, "right\n    {\n        type            empty"); print }' constant/polyMesh/boundary > tmp  
mv tmp constant/polyMesh/boundary


awk -v RS="\0" -v ORS="" '{ gsub(/(left)\n    {\n        type            patch/, "left\n    {\n        type            empty"); print }' constant/polyMesh/boundary > tmp  
mv tmp constant/polyMesh/boundary