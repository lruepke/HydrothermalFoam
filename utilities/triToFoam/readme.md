# triToFoam (OpenFOAM Foundation 10)

Converts Triangle's one-based .node/.ele/.edge files into one layer of prism
cells. Read the files by common basename: `triToFoam Triangle/box.node`.
`-zmin` and `-zmax` default to 0 and 1; `-keepOrientation` retains raw ordering.
Boundary markers map through optional .bm2name; element attributes map through
optional .attrib2name to cell zones/sets. Unmapped names retain Patch# / zone#. Without attributes, the default is zone1.
Front/back are separate empty patches named `front` and `back`; internal marked
edges retain the existing face-zone behavior.

In an activated Foundation 10 Bash shell:

```bash
cd utilities/triToFoam
wmake
```

Only finiteVolume, meshTools and dynamicMesh/OpenFOAM are required. Triangle
is a separate runtime mesher, not a link dependency. Obtain Triangle 1.6 from
[the author's distribution](https://www.cs.cmu.edu/~quake/triangle.html);
it is not vendored or installed by this repository. Check its separate license.
For a standalone temporary build: unpack triangle.zip and run
`cc -std=gnu89 -O2 -DNO_TIMER triangle.c -lm -o triangle`; put it on PATH.

A reproducible conversion and solver example shares the Gmsh cookbook's fields:
[gmsh2DBox](../../tutorials/cookbooks/2d/gmsh2DBox/README.md). Its Triangle commands
are independent of Gmsh. Run only in a fresh case copy; do not clean source cases.

Provenance: source and Make files copied from openfoam-7 at
b3815b5408f1b8f52a350dd5cc5b3c995fb3eb9f. That API already compiles on OF10;
only the mapping-reader blank/EOF guard and default ID for unattributed triangles
were corrected. Mesh topology, options, file formats and patch conventions are
unchanged. The historical branch is untouched. Legacy CMake/IDE files and the
large historical test case are not needed for this wmake port.
