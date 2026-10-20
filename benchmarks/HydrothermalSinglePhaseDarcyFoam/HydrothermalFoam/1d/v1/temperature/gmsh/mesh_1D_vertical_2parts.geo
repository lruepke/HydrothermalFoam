lc=5;

xmin=0;
xmax=10;
ymin=-300;
ymax=0;
z=0;
hpipe=100;

Point(1)={xmin,ymin,z,lc};
Point(2)={xmax,ymin,z,lc};
Point(3)={xmax,ymax,z,lc};
Point(4)={xmin,ymax,z,lc};

Point(5)={xmin,ymin+hpipe,z,lc};
Point(6)={xmax,ymin+hpipe,z,lc};


Line(1) = {1, 2};
//+
Line(2) = {2, 6};
//+
Line(3) = {6, 3};
//+
Line(4) = {3, 4};
//+
Line(5) = {4, 5};
//+
Line(6) = {5, 1};
//+
Line(7) = {5, 6};
//+
Line Loop(1) = {5, 7, 3, 4};
//+
Plane Surface(1) = {1};
//+
Line Loop(2) = {6, 1, 2, -7};
//+
Plane Surface(2) = {2};


Physical Point(101)={1};
Physical Point(102)={2};
Physical Point(103)={3};
Physical Point(104)={4};

Physical Line(201)={1};
Physical Line(202)={2,3};
Physical Line(203)={4};
Physical Line(204)={5,6};

Physical Surface(1)={1};
Physical Surface(2)={2};

// Transfinite Surface {1} Right;
// Recombine Surface {1};//+