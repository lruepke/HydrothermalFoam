//+
SetFactory("OpenCASCADE");
lc = 50;
lcmin=6;
ymin = -400;
y_pipe_top = -300;

radius_pipe=50;
height_pipe=100;
radius_layer1=600;
height_layer1=300;

Cylinder(1) = {0, ymin, 0, 0, height_pipe, 0, radius_pipe, 2*Pi};

Cylinder(2) = {0, y_pipe_top, 0, 0, height_layer1, 0, radius_layer1, 2*Pi};

Cylinder(3) = {0, y_pipe_top, 0, 0, height_layer1, 0, radius_pipe, 2*Pi};

BooleanDifference(4) = { Volume{2}; Delete; }{ Volume{3}; Delete; };

Cylinder(5) = {0, y_pipe_top, 0, 0, height_layer1, 0, radius_pipe, 2*Pi};
// make intersect surface unique
v() = BooleanFragments{ Volume{4}; Delete; }{ Volume{1,5}; Delete; };

s() = Unique(Abs(Boundary{ Volume{4}; }));
l() = Unique(Abs(Boundary{ Surface{s()}; }));
p() = Unique(Abs(Boundary{ Line{l()}; }));
Characteristic Length{p()} = lc;

s() = Unique(Abs(Boundary{ Volume{1,5}; }));
l() = Unique(Abs(Boundary{ Surface{s()}; }));
p() = Unique(Abs(Boundary{ Line{l()}; }));
Characteristic Length{p()} = lcmin;

// boundary surface
Physical Volume("layer2A") = {4,5};
Physical Volume("layer2B") = {1};
Physical Surface("sidewalls") = {1, 3, 5};
Physical Surface("bottom") = {7};
Physical Surface("top") = {2, 8};

Color Red{Surface{7};}
Color Green{Surface{1, 3, 5};}
Color Blue{Surface{2, 8};}
Color Purple{Volume{4,5};}
Color Yellow{Volume{1};}
