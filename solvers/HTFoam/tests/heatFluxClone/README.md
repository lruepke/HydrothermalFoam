# HydrothermalHeatFlux: OpenFOAM 10 copy/clone regression

This directory covers the HeatFlux part of the boundary-cloning commit, separate
from conductivity. Its production edit is in HydrothermalHeatFluxFvPatchScalarField.H:
plain copying is explicitly deleted and the obsolete no-argument clone() overload
is removed. The constructor taking an internal field and clone(iF) are unchanged.
There are no equation, conductivity, other BC, or solver-control changes here.

OpenFOAM Foundation 10 fvPatchField/fixedGradientFvPatchField disallow plain copy.
GeometricBoundaryField copies use clone(field); the base no-argument clone is an
unsupported NotImplemented route. Do not revive the old plain constructor or
silently retain its original internal-field reference.

## Reproduce the focused regression

From the repository root in bash, with an unused absolute run directory:

```bash
source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc
clone_run="$PWD/solvers/HTFoam/tests/heatFluxClone/run-NEW"
bash solvers/HTFoam/tests/heatFluxClone/build.sh "$clone_run"
ulimit -c 0
python3 solvers/HTFoam/tests/heatFluxClone/run_tests.py --run "$clone_run"
```

The build script copies sources before building. It never replaces an installed
library/executable and refuses an existing output directory. The default library
contains only HydrothermalHeatFlux, allowing this class's linking contract to be
tested independently of unrelated legacy BC defects. The platform linker options
are strict (`-undefined error` on macOS, `--no-allow-shlib-undefined` on Linux).
No allow-undefined workaround is used for these checks.

The test checks:

1. A compiled static assertion rejects plain copy constructibility.
2. nm/c++filt finds no unresolved plain HeatFlux copy-constructor symbol.
3. Explicit plain copying and typed no-argument cloning fail at compile time,
   with the expected deleted-constructor/missing-argument diagnostic.
4. The explicit-internal-field constructor, clone(iF), and ordinary volume-field
   copying preserve type, patch, values, gradient and serialized configuration.
5. A clone evaluates against its new owner's internal cells after those values
   change, while the original field remains unchanged. Runtime checks cover legacy
   dictionary mode and explicit conductivity-field mode.

No old solver executable, h1 snapshot, xThermo or solver build is required by this
focused test. --legacy-only exercises just the pre-conductivity BC contract.
HEATFLUX_BC_SOURCE can select an isolated alternate source tree for the build.

## Completed verification

- macOS: run-macos-component — strict component build/link, static assertion,
  two negative compilation checks and both runtime modes pass (5 recorded checks).
- Linux ARM64 / Foundation 10, cached image
  lruepke/hydrothermalfoam-openfoam10:2026.10-arm64: strict component build/link
  and the same 5 checks pass, with no permissive linker flags.
- The fix alone, applied to HEAD e244ea92 before conductivity changes, also passes
  normal Linux component build/link and 4 legacy-only checks. Evidence/source
  snapshots: run-review/linux/run-base. The current-source Linux run is run-current.
- The full boundary library, HTFoam and conductivity probe were rebuilt in
  ../conductivity/run-copyfix. All existing 22 serial, 4 MPI and 1 cyclic checks
  pass, including 9125-step h1 byte comparison, layered conduction, restart,
  nonuniform-flux mapping and rank-local failure diagnostics.

Original investigation evidence remains in ../conductivity/run-clone-investigation.
It reproduced the old and pre-fix updated libraries' runtime failures and Linux
link failures. New logs/source snapshots remain ignored under run-*/.
An initial macOS negative-test parser expected GCC's "no matching" wording;
it now also accepts Clang's "too few arguments", without relaxing failure checks.

## Historical full-library limitation (resolved by the pressure-BC increment)

At the time of the HeatFlux-only fix, strict Linux linking of the complete library
still failed on plain-copy symbols in noFlux, HydrothermalMassFluxPressure and
submarinePressureFvPatchScalarField. That failure is retained in
run-review/linux/run-full-library-link-failure. The subsequent narrowly scoped
[boundaryClones increment](../boundaryClones/README.md) deletes those unsupported
constructors/overloads and verifies strict linking plus ldd -r of the complete
library. The default test here remains component-isolated; use the complete-library
suite for integration verification.

## Commit separation

The cloning commit groups the four shared BC header corrections, this focused test
suite, the boundaryClones complete-library suite and related status documentation.
Conductivity field/heat-flux changes are in the preceding feature commit. Historical
run-review/copy-fix-only.patch verifies that the HeatFlux header correction also
works independently on the pre-conductivity source. No run artifacts are committed.
