# HTFoam benchmarks

One maintained OpenFOAM case per benchmark. Runs use fresh copies; source cases
and existing results are never cleaned or overwritten. Use the repository's
[Conda/Poetry setup](../../readme.md#python-environment): `environment.yaml` supplies
Python 3.13 and Poetry; the root `pyproject.toml` and `poetry.lock` manage NumPy and
Matplotlib. The older `requirements-benchmarks.txt` records earlier assessment
versions; it is not the setup workflow. Activate OpenFOAM Foundation 10 in **bash**
and use the current HTFoam-review executable and its matching boundary library.

```bash
# From the repository root, after the root Python setup:
conda activate py313_htf
# macOS OpenFOAM activation; use your installation's bashrc elsewhere.
source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc
cd benchmarks/HTFoam
export HTFOAM_SOLVER=/absolute/path/to/HTFoam-review
export HTFOAM_LIBRARY=/absolute/path/to/libHydrothermalBoundaryConditions.so
# On macOS the matching library normally has a .dylib suffix.

poetry run python run.py --case h1 --output work/h1
poetry run python run.py --case h2 --output work/h2
poetry run python run.py --case h3 --output work/h3
poetry run python run.py --case v1 --output work/v1
poetry run python run.py --case v2 --output work/v2
poetry run python run.py --case v3 --output work/v3
poetry run python run.py --case 2d --output work/2d
```

Add `--prepare-only` to inspect inputs without running; replace it with `--resume`
to execute, keeping the other arguments. Existing output directories are otherwise
refused. Each case also has a small `run.sh` forwarding to this same driver.
Only the 2D benchmark supports `--until-year 5000`, `15000` or `50000`; `--resume`
continues through the remaining accepted stages. v2 automatically performs its
accepted final 7.5-day step. No timestep, coupling or EOS tuning is performed.

Driver preflight/preparation checks (no solver run):
`poetry run python -m unittest discover -s tests -v`.

| Case | Purpose | Full duration | Local full-run time (approx.) |
|---|---|---|---:|
| h1 | Horizontal thermal transport; compatibility baseline | 250 legacy 365-day years | 6 s |
| h2 | Horizontal transport; aligned 198-cell, four-pass, 5-day configuration | 120 Julian years | 23 s |
| h3 | Horizontal low-pressure hot-water/vapour transport | 1500 Julian years | 100 s |
| v1 | Forced vertical liquid/gravity transport | 750 Julian years | 1 s |
| v2 | Forced hot/supercritical vertical transport | 350 Julian years | 27 s |
| v3 | Forced vertical vapour/gravity transport | 1500 Julian years | 118 s |
| 2d | Published 9 x 3 km buoyancy-driven circulation | 50 kyr, snapshots at 5/15/50 kyr | runner dependent |

The 2D case has the **original top at y=0**, not the boundary-aligned sensitivity
geometry. Basal step heating, material properties and all accepted numerical
settings are retained. Horizontal and vertical 1D cases are separate physical
families; the latter are not closed hydrostatic columns.

## Compare and plot pressure and temperature

Run these commands from this directory, in the same project environment:

```bash
poetry run python postprocess/compare_1d.py --case h1 --run work/h1 --output plots/h1
poetry run python postprocess/compare_1d.py --case h2 --run work/h2 --output plots/h2
poetry run python postprocess/compare_1d.py --case h3 --run work/h3 --output plots/h3
poetry run python postprocess/compare_1d.py --case v1 --run work/v1 --output plots/v1
poetry run python postprocess/compare_1d.py --case v2 --run work/v2 --output plots/v2
poetry run python postprocess/compare_1d.py --case v3 --run work/v3 --output plots/v3
poetry run python postprocess/plot_2d.py --run work/2d --time 5000 --output plots/2d-5k
poetry run python postprocess/plot_2d.py --run work/2d --time 15000 --output plots/2d-15k
poetry run python postprocess/plot_2d.py --run work/2d --time 50000 --output plots/2d-50k
```

Each new plot directory contains `comparison.png`, `comparison.pdf`, `profiles.csv`
and `metrics.json`. References are selected automatically. Existing historical runs
with a `case/` subdirectory are supported; 1D also accepts `--sample FILE` instead
of `--run`. Comparisons require matching times and use the original interpolation,
units and boundary masks, with no pressure fitting or coordinate shifts.

Original HYDROTHERM inputs and historical profiles remain under
`USGS_HYDROTHERMAL/`. The frozen vertical and 2D final tables make the comparisons
usable without rebuilding HYDROTHERM; identities and origins are recorded in
[PROVENANCE.txt](USGS_HYDROTHERMAL/PROVENANCE.txt). All pressures are absolute.

## Scope and limits

These are regression comparisons, not exact analytical solutions. EOS and spatial
stencils differ between HTFoam and HYDROTHERM. h1 retains its historical time
convention and initialization warning; h3 retains steady pressure initialization.
The v2 front discrepancy remains unresolved. v3's EOS-mass storage discrepancy
**decreases under timestep refinement but is not demonstrated converged and is
not an acceptable conservation tolerance**. No conservation claim follows from
the p/T plots. Weekly use is appropriate for repeatability/EOS/completion checks;
scientific convergence and mass/energy qualification remain separate work.

The existing `HydrothermalFoam/3d/` model definitions are retained unchanged.
They require separate mesh/solver qualification and are not advertised as runnable
with the current single-phase executable by this driver.

The [two-layer permeability benchmark](HydrothermalFoam/2d-layered/README.md)
uses one source case: `run.py --case 2d-layered`, optionally `--refine` for
180 x 60 rather than 90 x 30. Conductivity is uniformly 2 W/(m K), with a
10:1 permeability jump at y=-1100 m and harmonic Darcy mobility. Runs stop
at 5 kyr. Supply explicit HYDROTHERM reference CSVs to `plot_2d.py --case
2d-layered`; primary errors exclude the upper 300 m. The ordinary thermal
boundary discretizations remain different. This additional permeability check
does not replace the seven established cases or homogeneous 2D reference.

Legacy formulations, retired research diagnostics and their full instructions are
preserved in Git history and a verified local source archive outside this maintained
tree. All prior ignored runs, binaries, plots and environments remain in place.
