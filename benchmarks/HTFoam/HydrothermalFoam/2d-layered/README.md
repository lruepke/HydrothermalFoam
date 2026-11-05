# Sharp permeability-jump benchmark

9 x 3 km, uniform 90 x 30 cells, one metre thickness. K is 1e-15 m2 below
**y=-1100 m**, 1e-14 above. Bulk conductivity is uniformly 2 W/(m K).
Porosity=.1; rock density/Cp=2700/880 SI; gravity=9.81 m/s2; pure-water IAPS84.
Basal heating is 5 W/m2 on x=4000..5000 m, .05 elsewhere except the two
100 m end strips (zero), totalling **5390 W/m**.

Use the root Conda/Poetry environment and source OpenFOAM 10 in bash; provide
HTFOAM_SOLVER and HTFOAM_LIBRARY as described in the benchmark root README.
From benchmarks/HTFoam:

```bash
poetry run python run.py --case 2d-layered --output /tmp/layered
poetry run python run.py --case 2d-layered --refine --output /tmp/layered-fine
poetry run python tests/check_layered.py --output /tmp/darcy-check
poetry run python postprocess/plot_2d.py --case 2d-layered --run /tmp/layered \
  --time 5000 --reference /path/reference-5000yr.csv \
  --interface-reference /path/interface-5000yr.csv --output /tmp/layered-plot
```

`--prepare-only` copies inputs without running. `--refine` generates 180 x 60
private inputs, preserving the exact interface, heater edges/total power and
initial cold 100 m band. There is one maintained source case. Each prepared
run includes the corresponding official HYDROTHERM `reference.input`.
Eight Picard passes; Euler; maximum HT timestep one Julian year; stop at 5 kyr.
HYDROTHERM's .5-year balance cadence also limits its actual timestep.
Harmonic `interpolate((rho*(permeability|mu)))` applies to the actual pressure
mobility; existing default interpolation is unchanged for other cases.

Ordinary top boundaries: HT inletOutlet T (5 C inflow), fixed pressure;
HY IBC=10 with associated 5 C inflow enthalpy, including both corners.
The common external datum is 30 MPa at y=0, rho_external=1014.19371025668 kg/m3.
HT imposes 30 MPa at its face; HY imposes 304.974620148809 bar at y=-50 m
(302.4873100744045 bar at -25 m on the fine grid). No internal constraints.
The node/face boundaries differ: HT can conduct heat during recharge; HY IBC10
has no external conductive flux. Primary p/T statistics exclude y>-300 m;
full-domain statistics remain separate. This is a permeability verification,
not a claim of identical thermal boundaries or spatial convergence.

The optional interface reference is CSV `x_m,j_up_kg_m2_s` at y=-1100 m,
with positive-upward **face** mass flux, not HY nodal plotting vectors. For
single-phase supercritical-pressure water, sum native printed water/steam
Darcy face fluxes and multiply by HY's density at mean adjacent p/h (official
avgvalue/tblookup); convert g/(cm2 s) to kg/(m2 s) by 10. Preserve extraction
provenance and printed precision with the reference. Integrated rates use
one metre thickness. The analytical checker independently tests constant-flux
transmissibility; shared FV faces cancel exactly, which alone does not prove
EOS inventory conservation. The existing finite-increment storage caveat remains.

5 kyr result: harmonic interface transmissibility is verified (analytical
interface-flux error <=2.2e-12 relative), and the discrete interface flux is
continuous by the shared finite-volume face. Coarse-grid cross-code gross
upward flow differs by **1.23%**: 4.5943e-4/4.6517e-4 kg/s (HT/HY, 1 m
thickness). Face-profile RMS/max differences are 1.905e-9/6.647e-9 kg/(m2 s).
Interior p/T RMS/max: 2.184/8.777 kPa and .362/3.248 C. HT refinement raises
upward/downward flow by 6.40/8.76%; no spatial-convergence claim. The 50 C
front remains below the interface. Sharp-jump transmissibility is supported;
hot-plume passage and EOS inventory conservation remain unqualified.
