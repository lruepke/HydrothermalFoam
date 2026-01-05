SetFactory("OpenCASCADE");
lcmin=10;
R=1000;
r=600;
x0=0;
y0=0;
z0=0;
zmax=10;
Circle(1) = {x0,y0,z0, R, 0, 2*Pi};
Circle(2) = {x0,y0,z0, r, 0, 2*Pi};
//+
Curve Loop(1) = {1};
//+
Curve Loop(2) = {2};
//+
Plane Surface(1) = {1, 2};

// refine
l() = Unique(Abs(Boundary{ Surface{1}; }));
p() = Unique(Abs(Boundary{ Line{l()}; }));
Characteristic Length{p()} = lcmin;

Extrude {0, 0, zmax} {
Surface{1};
Layers{1};
Recombine;
}

Physical Volume("crust") = {1};
Physical Surface("frontAndBack") = {1,4};
Physical Surface("bottom") = {3};
Physical Surface("seafloor") = {2};