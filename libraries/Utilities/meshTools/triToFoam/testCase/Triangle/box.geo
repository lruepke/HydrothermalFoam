// 0. define some variables
xmin=0;
xmax=2000;
ymin=-3000;
ymax=-2000;
zmin=0;
zmax=10;
lc=10;
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

p_control = newp;
Point(p_control) = {(xmin+xmax)/2.0, (ymin+ymax)/2.0, zmin, lc};
// control the cell size for a region
Physical Point("Control")={p_control};

Physical Line("BoundaryLine1")={1};
Physical Line("BoundaryLine2")={2};
Physical Line("BoundaryLine3")={3};
Physical Line("BoundaryLine4")={4};