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

Cylinder(1) = {0, ymin, 0, 0, height_pipe+20, 0, radius_pipe, 2*Pi};

Cylinder(2) = {0, y_pipe_top, 0, 0, height_layer1, 0, radius_layer1, 2*Pi};

BooleanUnion(4) = { Volume{2}; Delete; }{ Volume{1}; Delete; };