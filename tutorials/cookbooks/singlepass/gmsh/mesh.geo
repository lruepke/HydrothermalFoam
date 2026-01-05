SetFactory("OpenCASCADE");
lc = 50;
lcmin=10;
z=0;
zmin=-5;
xmin=0;
xmax=2000;
ymax=-3000;
ymin=-4000;
width_left=300;
width_bottom=75;
width_right=75;
xmin_lowPerm=xmin+width_left;
xmax_lowPerm=xmax-width_right;
ymax_lowPerm=ymax;
ymin_lowPerm=ymin+width_bottom;
//second lim 
width_left_secondlim=width_left/3;
width_bottom_secondlim=width_left_secondlim/2;
x1_min_secondlim=720;
x2_min_secondlim=x1_min_secondlim+width_left_secondlim;
y1_min_secondlim=ymax-50;
y2_min_secondlim=y1_min_secondlim-width_bottom_secondlim;

//points
Point(1) = {xmin,ymin,z, lc};
Point(2) = {xmax,ymin,z, lc} ;
Point(3) = {xmax,ymax,z, lc} ;
Point(4) = {xmin,ymax,z, lc} ;
//new points: low permeability zone
Point(5) = {xmin_lowPerm,ymin_lowPerm,z, lc};
Point(6) = {xmax_lowPerm,ymin_lowPerm,z, lc} ;
Point(7) = {xmax_lowPerm,ymax_lowPerm,z, lc} ;
Point(8) = {xmin_lowPerm,ymax_lowPerm,z, lc} ;
Point(9) = {xmax_lowPerm,ymin,z, lc} ;
//second lim
Point(10)={x1_min_secondlim,ymax,z,lc};
Point(11)={x2_min_secondlim,ymax,z,lc};
Point(13)={x1_min_secondlim,y2_min_secondlim,z,lc};
Point(14)={x2_min_secondlim,y1_min_secondlim,z,lc};
Point(15)={xmax_lowPerm,y2_min_secondlim,z,lc};
Point(16)={xmax_lowPerm,y1_min_secondlim,z,lc};
Point(17)={xmin+width_left,ymin,z,lc};
Point(18)={xmin,ymin+width_bottom,z,lc};
Point(19)={xmax,ymin+width_bottom,z,lc};

//+
Line(3) = {9, 6};
//+
Line(4) = {6, 15};
//+
Line(5) = {15, 13};
//+
Line(6) = {13, 10};
//+
Line(8) = {8, 4};
//+
Line(9) = {8, 5};
//+
Line(10) = {5, 6};
//+
Line(11) = {15, 16};
//+
Line(12) = {16, 7};
//+
Line(13) = {16, 14};
//+
Line(14) = {14, 11};
//+
Line(15) = {11, 10};
//+
Line(17) = {7, 3};
//+
Line(19) = {2, 9};

//+
Line(20) = {1, 17};
//+
Line(21) = {17, 5};
//+
Line(22) = {5, 18};
//+
Line(23) = {17, 9};
//+
Line(24) = {2, 19};
//+
Line(25) = {19, 6};
//+
Line(26) = {19, 3};
//+
Line(27) = {1, 18};
//+
Line(28) = {18, 4};
//+
Line Loop(1) = {8, -28, -22, -9};
//+
Plane Surface(1) = {1};
//+
Line Loop(2) = {20, 21, 22, -27};
//+
Plane Surface(2) = {2};
//+
Line Loop(3) = {10, -3, -23, 21};
//+
Plane Surface(3) = {3};
//+
Line Loop(4) = {3, -25, -24, 19};
//+
Plane Surface(4) = {4};
//+
Line Loop(5) = {26, -17, -12, -11, -4, -25};
//+
Plane Surface(5) = {5};


//refine
// 1. discharge zone
Point(200) = {xmax-width_right/2, ymin, z, lc};
Point(201) = {xmax-width_right/2, ymax, z, lc};
Line(200)={200,201};
Field[1] = Attractor;
Field[1].NNodesByEdge = 400;
Field[1].EdgesList = {200};

Field[2] = Threshold;
Field[2].IField = 1;
Field[2].LcMin = lc/10; // minimum cell size is 2m
Field[2].LcMax = lc;
Field[2].DistMin = width_right*3;
Field[2].DistMax = width_right*8;

// 2. bottom heat source zone
Point(300) = {xmin, ymin+width_bottom/2, z, lc};
Point(301) = {xmax-width_right, ymin+width_bottom/2, z, lc};
Line(300)={300,301};
Field[11] = Attractor;
Field[11].NNodesByEdge = 400;
Field[11].EdgesList = {300};

Field[12] = Threshold;
Field[12].IField = 11;
Field[12].LcMin = lc/5; // minimum cell size is 2m
Field[12].LcMax = lc;
Field[12].DistMin = width_bottom;
Field[12].DistMax = width_bottom*2;

Field[7] = Min;
Field[7].FieldsList = {2,12};
Background Field = 7;

Extrude {0, 0, zmin} {
    Surface{1:5};
    Layers{1};
    Recombine;
    }//+

Physical Volume("rechargeZone") = {1};
Physical Volume("dischargeZone") = {2,3,4,5};
Physical Surface("frontAndBack") = {1:5, 10,14,18,28, 22};
Physical Surface("wall") = {7, 13, 9, 15, 27, 26, 25, 23, 20};
Physical Surface("bottom") = {11, 17,21};
Physical Surface("top") = {6, 24};

Color Gray{Surface{1:5, 10,14,18,28, 22};}
Color Green{Surface{7, 13, 9, 15, 27, 26, 25, 23, 20};}
Color Red{Surface{11, 17, 21};}
Color Blue{Surface{6, 24};}
