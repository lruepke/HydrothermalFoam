lc=5;

xmin=0;
xmax=10;
ymin=-2000;
ymax=0;
z=0;
zmin=-100;
Point(1)={xmin,ymin,z,lc};
Point(2)={xmax,ymin,z,lc};
Point(3)={xmax,ymax,z,lc};
Point(4)={xmin,ymax,z,lc};

Line(1)={1,2};
Line(2)={2,3};
Line(3)={3,4};
Line(4)={4,1};

Line Loop(1)={1,2,3,4};
Plane Surface(1)={1};

Extrude {0, 0, zmin} {
    Surface{1};
    Layers{1};
    Recombine;
    }
Transfinite Surface {1} Right;
Recombine Surface {1};//+

// Physical Volume("layer2A") = {1,2,3};
// Physical Volume("layer2B") = {4};
Physical Volume("internal") = {1};
Physical Surface("frontAndBack") = {1,26};
Physical Surface("left") = {25};
Physical Surface("right") = {17};
Physical Surface("top") = {21};
Physical Surface("bottom") = {13};
