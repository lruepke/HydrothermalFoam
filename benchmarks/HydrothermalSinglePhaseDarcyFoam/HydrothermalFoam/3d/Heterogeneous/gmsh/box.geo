xmin=-4500;
xmax=4500;
ymin=-3000;
ymax=0;
zmin=-4500;
zmax=4500;
width_heatsource=1000;
x0_heatsource=0;
lc=100;
lc_c=100;
Point(1) = {xmin, ymax, zmax, lc};
Point(2) = {xmax, ymax, zmax, lc};
Point(3) = {xmax, ymin, zmax, lc};
Point(4) = {xmin, ymin, zmax, lc};
//+
Line(1) = {4, 3};
//+
Line(2) = {3, 2};
//+
Line(3) = {2, 1};
//+
Line(4) = {1, 4};
//+
Line Loop(1) = {3, 4, 1, 2};
//+
Plane Surface(1) = {1};

Transfinite Surface {1};
Recombine Surface {1};

Extrude {0, 0, -zmax+zmin} {
Surface{1};
Layers{90};
Recombine;
}
Physical Volume("internal") = {1};

Physical Surface("sides") = {1,26,17,25};
Physical Surface("bottom") = {21};
Physical Surface("top") = {13};
Color Red{Surface{21};}
Color Green{Surface{1,26,17,25};}
Color Blue{Surface{13};}

