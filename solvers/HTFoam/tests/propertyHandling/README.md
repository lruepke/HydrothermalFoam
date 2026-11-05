# xThermo property-handling verification

Isolated tests for the five-file property-handling increment, 2026-10-29.
No preserved benchmark is cleaned or rerun. Generated runs are ignored by Git but
remain on disk. Copy their evidence explicitly when transferring this review.

## Reproduce in a fresh directory

From the repository root in **bash**, using an unused absolute run path:

```bash
source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc
export xThermo_DIR=$HOME/git-geomar/xThermo/install-master
property_run="$PWD/solvers/HTFoam/tests/propertyHandling/run-NEW"
mkdir -p "$property_run/bin"
export FOAM_USER_APPBIN="$property_run/bin"
(cd solvers/HTFoam && wmake)
(cd solvers/HTFoam/tests/propertyHandling/probe && wmake)
ulimit -c 0
python3 solvers/HTFoam/tests/propertyHandling/run_tests.py --run "$property_run"
python3 solvers/HTFoam/tests/propertyHandling/run_tests.py --run "$property_run" --mpi
```

The default run requires no local baseline snapshot or old executable. The runner
uses the tracked input-only h1 case and [small text fixtures](fixtures/h1-old/PROVENANCE.md).
It verifies fixture checksums, then numerically compares the full h1 result with
reference cell properties, internal face flux, and the sampled profile. Tolerance
is 5e-6 times the maximum reference magnitude per quantity (profile coordinates:
1e-12), allowing margin over six-digit output rounding. This is a regression limit,
not scientific validation or an EOS accuracy claim.

The runner refuses to overwrite an existing cases directory. MPI needs local
sockets. Original cases and preserved snapshots are never cleaned or modified.
For the stricter same-host byte comparison, explicitly supply a full snapshot:

```bash
python3 solvers/HTFoam/tests/propertyHandling/run_tests.py --run "$property_run" \
  --baseline /path/to/baseline-old --preserve /path/to/old/HTFoam
```

Choose a fresh run directory for this additional invocation. `--baseline` requires
`case/` and its SHA256SUMS manifest; `--preserve` is repeatable for additional files
or directories. Without these options, there are no machine-specific artifact or
home-directory requirements. All numerical tests still require installed OpenFOAM
10 and the reviewed xThermo installation; the probe and solver are built as above.

## Completed run: `run-20261029/`

- wmake and fresh CMake builds passed; both produced separate executables.
- The CMake executable also completed a valid hot-brine startup/time-loop smoke.
- Nonzero salinity X=0.1, T=573.15 K, p=30 MPa: both IAPS84 and IAPWS95 solver
  fields agree with direct guarded EOS evaluation to relative tolerance 1e-12.
  IAPS84 density is within 0.001 kg/m³ of the published CLI check 849.034.
- Invalid p/X/T, bad backend, cold IAPWS95 brine domain failure, a real unavailable
  IAPS84 viscosity, actual multiphase state, and an invalid physical boundary
  all terminate as expected. Boundary diagnostics identify patch/face/centre.
- Real low-pressure liquid brine at 323.15 K, 1 bar, X=0.26 is rejected for
  betaT=-2.826877337590522e-10 1/Pa. This is solver-domain rejection of a documented
  correlation limitation, not correction/clipping of library results.
- Real vapour, supercritical water, and negative-expansivity cold water are accepted.
- The probe checks NaN input, status failures, a propagated standard exception,
  unusable properties, exact Critical/solid/Unknown rejection, negative/zero alpha
  acceptance, and the two additional supercritical enumeration names. Fault-injected
  checks test guard policy, not accuracy of those synthetic EOS states.
- A cyclic brine case runs successfully; its positive starting time avoids testing
  the unrelated steady all-Neumann initialization singularity.
- Two-rank nonuniform thermal/pressure-driven brine agrees with serial: maximum
  relative differences p 4.10e-11, T 0, rho 1.89e-12, mu 2.72e-12,
  U/phi 2.74e-9. Test limits are 1e-9 for p/T/properties and 1e-6 for U/phi.
- A bad state solely on rank 1 aborts the MPI job without hanging (30-second timeout).
- Full 9125-step h1 regression: sampled profile and final p/T/U/rho/mu/phi files are
  byte-identical to the original baseline at its saved precision.
- h1 PNG/PDF/JSON comparisons are in `h1-comparison/`. HYDROTHERM RMSE remains
  3.28287648 °C and 0.155478441 MPa; new-minus-old sampled errors are zero.
- All previously saved baseline files and executables pass preservation checks.

Evidence: `results.json`, `mpi-results.json`, `additional-results.json`, build logs,
individual case logs, `increment.patch`, `provenance.json`, and `preserved-sha256.json`.
These artifacts describe the original verification run, before the commit preparation.
They remain local; the compact tracked fixture contains only reference data and provenance.

## Test development notes and limits

An initial 8-cell smoke mesh was too small for the retained GAMG settings; test
meshes use 40 cells. An initial probe output parser exposed quoted Foam strings;
diagnostics now print unquoted context. Initial static MPI tests encountered
normalized pressure residual stagnation at roundoff-sized updates; the final MPI
case uses a small pressure gradient and does not reach the iteration limit. The
sandbox blocked OpenMPI sockets; the successful MPI runs were outside it. Earlier
attempts/logs were retained under separately named directories.

These tests establish the guard behavior and limited regressions, not broad EOS
accuracy, mesh convergence, coupled-interface phase equilibrium, initialization
convergence, or energy conservation. No extrapolation restrictions beyond the
advertised model envelope were introduced. EOS limits and known scientific defects
still apply. Exact Critical and nonpositive betaT are now unsupported by policy.
The zero-valued startup field storage is filled before any equation or flux use;
it is not a fallback property state.

## Commit preparation verification

The staged source/input/fixture files were exported to an isolated checkout under
`run-commit-prep/clean-checkout`, without `baseline-old/` or `review-new/`. Existing
tested binaries (matching the unchanged solver source hashes) were copied into
fresh run directories. Default serial checks (31) and MPI checks (2) passed with
no baseline argument. A separate 32-check serial run with `--baseline` also passed,
including byte comparisons of all six principal final fields and the profile.
Copied input files have trailing whitespace normalized; numerical settings are
unchanged. All original artifacts and executables remain checksum-identical.
