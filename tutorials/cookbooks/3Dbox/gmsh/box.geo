// 0. define some variables
xmin=0;
xmax=2000;
ymin=-3000;
ymax=-2000;
zmin=0;
zmax=xmax;
lc=25;
// 1. define points
Point(1) = {xmin, ymax, zmin, lc};
Point(2) = {xmax, ymax, zmin, lc};
Point(3) = {xmax, ymin, zmin, lc};
Point(4) = {xmin, ymin, zmin, lc};
// 2. define lines
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};
// 3. define line loop and surface
Line Loop(6) = {4, 1, 2, 3};
Plane Surface(6) = {6};
// // 3.1 make regular mesh
// Transfinite Surface {6};
// Recombine Surface {6};
// 4. extrude 2D surface to a 3D volume
Extrude {0, 0, zmax} {
Surface{6};
Layers{80}; //set layer number to 1 for 2D model
Recombine;
}
// 5. define boundary patches via Physical keyword
Physical Surface("frontAndBack") = {28,6};
Physical Surface("bottom") = {27};
Physical Surface("left") = {15};
Physical Surface("top") = {19};
Physical Surface("right") = {23};
// 6. specify a name for cell region which is used for 'setFields'
Physical Volume("internal") = {1};
// 7. specify different color for different boundary patches
Color Gray{Surface{28, 6};}
Color Red{Surface{27};}
Color Purple{Surface{15};}
Color Pink{Surface{23};}
Color Blue{Surface{19};}
Color Green{Volume{1};}