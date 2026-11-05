# gmsh2DBox

## Prepare, run, visualize

Activate OpenFOAM Foundation 10 **in Bash** (on this Mac:
`source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc`). Use the reviewed executable
and its matching boundary library; on Linux the library ends in `.so`, on macOS
in `.dylib`:

```bash
export HTFOAM_SOLVER=/absolute/path/to/HTFoam-review
export HTFOAM_LIBRARY=/absolute/path/to/libHydrothermalBoundaryConditions.dylib
mkdir -p "$HOME/HydrothermalFoam_runs"
# From the repository root; choose a new destination for every run.
cp -R tutorials/cookbooks/2d/gmsh2DBox "$HOME/HydrothermalFoam_runs/gmsh2DBox-smoke"
bash "$HOME/HydrothermalFoam_runs/gmsh2DBox-smoke/run.sh" --smoke
```

`--smoke` meshes and runs three fixed one-hour steps, writing each step. For the
original full duration use another fresh copy and omit `--smoke`. No cleaning is
performed. `--prepare-only` stops after mesh checks; then run `$HTFOAM_SOLVER`
from the prepared case. The script refuses execution in the tracked source case
or over an existing mesh. Open `case.foam` in ParaView; select the latest time,
color by T (K) or p (Pa), and use U (Darcy velocity, m/s) for flow visualization.
Runtime C++ compilation needs the compiler and OpenFOAM development headers.

Original 600 x 200 m domain, extruded 100 m, with uniform K=4e-14 m2,
5 C initial/recharge temperature, 200 C basal temperature and 20 MPa top pressure.
Both mesh routes use these same solver fields and boundary conditions. The legacy
setFieldsDict (1e-9 / 1e-13 zoning) is deliberately not invoked: it was disabled
in the original workflow and has no matching left cell zone in box.geo.

transportProperties copies porosity=.1, kr=1.5 W/(m K), rock rho=3000 kg/m3 and
Cp=880 J/(kg K) from the original thermophysicalProperties. The original fluid
is pure water; xThermo now uses H2O/IAPS84, replacing the freesteam-based IAPWS
model. This EOS compatibility change is explicit, not a claim of identical EOS
results. INIT retains one outer pass/two pressure correctors; its exhaustion
warning is expected, with no convergence target. Transient coupling is one pass.

## Independent mesh choices

Requires Gmsh on PATH (or Triangle plus triToFoam for the alternative).
Gmsh is the default; `gmsh/box.geo` is the complete source. Its physical surfaces
and one extrusion layer are unchanged. In a fresh case copy, the mesh commands
used by run.sh are:

```bash
cp 0/permeability.orig 0/permeability
gmsh gmsh/box.geo -3 -format msh22 -o gmsh/box.msh
gmshToFoam gmsh/box.msh
changeDictionary
checkMesh
```

For Triangle 1.6 plus the ported `triToFoam`, copy this same case to a new run
location, then `bash run.sh --triangle --smoke` (omit --smoke for full duration).
The independent mesh commands are:

```bash
cp 0/permeability.orig 0/permeability
triangle -pQIq20Aae Triangle/box.poly
triToFoam Triangle/box.node -zmin 0 -zmax 100
createPatch -overwrite -dict system/createPatchDictTriangle
changeDictionary
checkMesh
```

The .poly uses identical x/y bounds and <=50 m2 triangle area, comparable to the
Gmsh 10 m size, not an identical triangulation. Mapping files preserve the names
top/right/bottom/left and the internal cell zone. triToFoam's separate empty
front/back patches are combined into frontAndBack using standard createPatch;
no solver configuration is duplicated. Generated .msh/.node/.ele/.edge/polyMesh
files belong only in run copies. Build triToFoam with wmake as documented in
[its README](../../../../utilities/triToFoam/readme.md).

See [CaseConfiguration.md](../../../../solvers/HTFoam/CaseConfiguration.md) for the solver contract.
