# 3Dbox

Original 2 x 1 x 2 km box (x=0..2000, y=-3000..-2000, z=0..2000 m),
Gmsh size 25 m and 80 extrusion layers. The Gaussian basal temperature
(573..873.15 K), cold 278.15 K recharge, top 30 MPa pressure, K=1e-14 m2,
kr=1.5 W/(m K), porosity=.1, rock rho=3000 kg/m3 and Cp=880 J/(kg K)
are unchanged. INIT explicitly remains disabled; three Picard passes and original
schemes, tolerances and full-duration timestep controls are retained.

**Approved salinity change:** xThermo H2O-NaCl/IAPS84 now uses X=0 instead of .2.
The original hot state (600 C, 30 MPa, X=.2) is vapor + halite, outside HTFoam's
single-phase formulation. The original input is preserved in Git history;
no geometry, heating or other settings were substituted from 3Dbox_par.

## Prepare, run, visualize

Activate OpenFOAM Foundation 10 in **Bash**, then select the reviewed executable
and matching boundary library (.so on Linux, .dylib on macOS). Requires Gmsh;
the optional parallel run also needs OpenMPI and the OpenFOAM parallel tools.
On macOS the script explicitly forwards the MPI Pstream library search path.
From the repository root:

```bash
# On this Mac: source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc
export HTFOAM_SOLVER=/absolute/path/to/HTFoam-review
export HTFOAM_LIBRARY=/absolute/path/to/libHydrothermalBoundaryConditions.dylib
mkdir -p "$HOME/HydrothermalFoam_runs"
cp -R tutorials/cookbooks/3Dbox "$HOME/HydrothermalFoam_runs/3Dbox-smoke"
bash "$HOME/HydrothermalFoam_runs/3Dbox-smoke/run.sh" --smoke
```

Smoke mode runs one fixed one-hour step on the original mesh. Use another fresh
copy with `--parallel --smoke` for two ranks, or omit --smoke for the original
full duration. `--prepare-only` generates/checks the mesh without running.
The scripts never clean and refuse the tracked source case or an existing mesh.
Open `case.foam` in ParaView; color by T (K) or p (Pa), and use U (m/s) for flow.
The original mesh is substantial: brief smoke qualification does not establish
long-time convection accuracy, timestep convergence or energy conservation.

See [CaseConfiguration.md](../../../solvers/HTFoam/CaseConfiguration.md).
