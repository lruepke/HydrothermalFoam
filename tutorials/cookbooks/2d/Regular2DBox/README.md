# Regular2DBox

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
cp -R tutorials/cookbooks/2d/Regular2DBox "$HOME/HydrothermalFoam_runs/Regular2DBox-smoke"
bash "$HOME/HydrothermalFoam_runs/Regular2DBox-smoke/run.sh" --smoke
```

`--smoke` meshes and runs three fixed one-hour steps, writing each step. For the
original full duration use another fresh copy and omit `--smoke`. No cleaning is
performed. `--prepare-only` stops after mesh checks; then run `$HTFOAM_SOLVER`
from the prepared case. The script refuses execution in the tracked source case
or over an existing mesh. Open `case.foam` in ParaView; select the latest time,
color by T (K) or p (Pa), and use U (Darcy velocity, m/s) for flow visualization.
Runtime C++ compilation needs the compiler and OpenFOAM development headers.

A 2 x 1 km, 100 x 50-cell convection box at y=-3500..-2500 m.
Original permeability 1e-14 m2, kr=1.5 W/(m K), rock rho=3000 kg/m3,
Cp=880 J/(kg K), porosity=.1. Original Gaussian basal temperature, cold recharge
and submarine pressure boundary are unchanged. The active EOS remains
H2O-NaCl/IAPS84 with X=0; thermophysicalProperties is retained as legacy provenance.

INIT is explicitly disabled, preserving the former nOuterCorrectors=0 behavior;
three Picard passes and original timestep controls/schemes are retained. This
is a teaching example, not a converged hydrostatic or quantitative reference.
submarinePressure uses elevation (top pressure 24.943825 MPa), not the saved
30 MPa value placeholder; its known rhoValue restart serialization limitation
is described in the solver configuration guide.

See [CaseConfiguration.md](../../../../solvers/HTFoam/CaseConfiguration.md) for the solver contract.
