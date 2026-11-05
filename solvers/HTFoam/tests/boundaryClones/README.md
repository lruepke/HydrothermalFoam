# Complete shared-boundary-library copy/clone regression

All three pressure BCs had the same obsolete contract as HydrothermalHeatFlux:
a declared but undefined plain copy constructor and a no-argument clone() that
called it. Their .C definitions had already been commented out for OpenFOAM 10.

This increment changes only the relevant declaration/clone blocks in:

- libraries/BoundaryConditions/noFlux/noFluxFvPatchScalarField.H
- libraries/BoundaryConditions/HydrothermalMassFluxPressure/HydrothermalMassFluxPressureFvPatchScalarField.H
- libraries/BoundaryConditions/SubmarinePressure/submarinePressureFvPatchScalarField.H

Plain constructors are explicitly deleted; no-argument clone() is removed.
Constructors with an internal-field reference, clone(iF), mapping constructors,
and every .C implementation remain unchanged. No pressure/flux/density formula,
dictionary parsing, serialization or solver controls are modified. The same commit
also records the separately approved HeatFlux copy fix and its focused tests.

## Reproduce

From the repository root in bash with a fresh absolute output path:

```bash
source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc
clone_run="$PWD/solvers/HTFoam/tests/boundaryClones/run-NEW"
bash solvers/HTFoam/tests/boundaryClones/build.sh "$clone_run"
ulimit -c 0
python3 solvers/HTFoam/tests/boundaryClones/run_tests.py --run "$clone_run"
```

The build copies and compiles the COMPLETE production library, all four BCs, in the
fresh ignored run directory. It reuses heatFluxClone's full-library build option
and builds the new pressure probe with strict linking. No permissive undefined-
symbol flag is used. Existing installed executables/libraries and old artifacts
are not overwritten. Tests refuse to overwrite case directories.

The existing five HeatFlux checks run against this complete library (results.json).
The ten additional checks (pressure-results.json) establish:

- All three classes are not plain-copy-constructible (compiled static assertions).
- The complete library has no unresolved plain-copy constructor for any of the
  four BCs; Linux additionally checks ldd -r for all unresolved dependencies.
- All six unsupported plain-copy/no-argument-clone calls fail during compilation,
  with the expected diagnostics, instead of remaining runtime/link traps.
- Each class's explicit-reference constructor, clone(iF) and ordinary volume-field
  copy preserve type, patch, internal-field reference, values, gradient and written
  configuration. After the new owner's cell values change, the clone evaluates
  against that owner, leaving the original unchanged.

Fixtures use four patch faces, non-default mobility/gravity-flux field names,
nonuniform prescribed mass flux (0.1/0.2/0.3/0.4), nonzero gravity, and non-default
rhoValue=1123. They exercise preserved settings when reevaluating clones, not a
new interpretation or scientific validation of those boundary formulas.

## Completed results

- macOS: run-macos; full library and both strict-linked probes built; 10 pressure/
  symbol/negative-compilation checks and 5 existing HeatFlux checks passed.
- Linux ARM64 / Foundation 10: cached image
  lruepke/hydrothermalfoam-openfoam10:2026.10-arm64, offline and with the repository
  mounted read-only; the full library and both clients link normally with
  --no-allow-shlib-undefined. All 15 checks pass, and ldd -r reports no unresolved
  symbols. Evidence is under run-review/linux/run-complete and log.linux.
- The full library, HTFoam and conductivity probe were rebuilt independently in
  ../conductivity/run-all-copyfixes. Existing 22 serial, 4 MPI and 1 cyclic checks
  pass, including complete h1 byte comparison, stationary restart, layered material
  processor-interface checks, nonuniform flux mapping and rank-local failures.

This resolves the three additional plain-copy symbols exposed by the earlier
HeatFlux-only fix. Unrelated pressure-BC issues (including dictionary round-trip
or dynamic-mesh mapping behaviour) are not fixed or certified by these tests.

No commits/pushes are made by these scripts. Production diffs and preservation
metadata remain local under run-review/. The accepted cloning corrections and
tests are committed separately from conductivity physics/build changes. Generated
run artifacts are excluded.
