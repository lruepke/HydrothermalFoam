# Regular2DBox_layered

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
cp -R tutorials/cookbooks/2d/Regular2DBox_layered "$HOME/HydrothermalFoam_runs/Regular2DBox_layered-smoke"
bash "$HOME/HydrothermalFoam_runs/Regular2DBox_layered-smoke/run.sh" --smoke
```

`--smoke` meshes and runs three fixed one-hour steps, writing each step. For the
original full duration use another fresh copy and omit `--smoke`. No cleaning is
performed. `--prepare-only` stops after mesh checks; then run `$HTFOAM_SOLVER`
from the prepared case. The script refuses execution in the tracked source case
or over an existing mesh. Open `case.foam` in ParaView; select the latest time,
color by T (K) or p (Pa), and use U (Darcy velocity, m/s) for flow visualization.
Runtime C++ compilation needs the compiler and OpenFOAM development headers.

Same original 2 x 1 km, 100 x 50 mesh and material properties as before:
kr=1.5 W/(m K), rock rho=3000 kg/m3, Cp=880 J/(kg K), porosity=.1.
Preparation copies permeability.orig then runs setFields: 1e-14 m2 below y=-3000 m,
1e-13 m2 above (2500 cells each). The case explicitly selects
`interpolate((rho*(permeability|mu))) harmonic` for Darcy mobility. This is the
intentional interface-discretization update; uniform conductivity stays linear.

H2O-NaCl/IAPS84, X=0, initial fields, basal fixed temperature, inletOutlet top,
submarine pressure and original timestep settings are retained. INIT remains
explicitly disabled, with three Picard passes. Top pressure is 24.943825 MPa;
see the configuration guide for the submarinePressure restart limitation.
This teaches permeability zoning; quantitative interface verification belongs
in benchmarks/HTFoam, not this laterally uniform convection example.

See [CaseConfiguration.md](../../../../solvers/HTFoam/CaseConfiguration.md) for the solver contract.
