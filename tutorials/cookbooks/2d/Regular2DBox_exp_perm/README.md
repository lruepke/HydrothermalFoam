# Regular2DBox_exp_perm

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
cp -R tutorials/cookbooks/2d/Regular2DBox_exp_perm "$HOME/HydrothermalFoam_runs/Regular2DBox_exp_perm-smoke"
bash "$HOME/HydrothermalFoam_runs/Regular2DBox_exp_perm-smoke/run.sh" --smoke
```

`--smoke` meshes and runs three fixed one-hour steps, writing each step. For the
original full duration use another fresh copy and omit `--smoke`. No cleaning is
performed. `--prepare-only` stops after mesh checks; then run `$HTFOAM_SOLVER`
from the prepared case. The script refuses execution in the tracked source case
or over an existing mesh. Open `case.foam` in ParaView; select the latest time,
color by T (K) or p (Pa), and use U (Darcy velocity, m/s) for flow visualization.
Runtime C++ compilation needs the compiler and OpenFOAM development headers.

Original 2 x 1 km, 100 x 50 mesh, H2O-NaCl/IAPS84 at X=0 and all physical
boundary conditions are retained. kr=1.5 W/(m K), rock rho=3000 kg/m3,
Cp=880 J/(kg K), porosity=.1. The original #codeStream compiles permeability
at read time: K=1e-14*exp((y-y_min_cell)/434.3) m2. This uses the lowest
**cell centre**, not the geometric bottom; K spans 1e-14..9.54965e-14 m2.
INIT remains disabled and three Picard passes are retained.
Darcy mass mobility uses `interpolate((rho*(permeability|mu))) harmonic`.
Uniform thermal conductivity retains linear face interpolation.

The basal 1273.15 K (1000 C) is unchanged. The current xThermo accepts the
startup hot state at 30 MPa as supercritical; the three-hour smoke passes the
solver's phase/property checks. This is at the H2O-NaCl model's upper temperature
limit: no clipping is applied, and longer runs remain unqualified. The cold top
and submarine pressure use the original convention (24.943825 MPa at the top).

See [CaseConfiguration.md](../../../../solvers/HTFoam/CaseConfiguration.md) for the solver contract.
