# HTFoam: technical background and modernization handoff

Prepared 2026-10-29 for an AI assisting and supervising the modernization.
This document is self-contained context, not permission to perform further work.
Paths are relative to the HydrothermalFoam repository unless stated otherwise.
Updated after commit preparation on 2026-10-29. Source observations describe the
current property-handling implementation; evidence includes the original 2026-10-28
h1 runs and 2026-10-29 targeted/regression verification. No governing-equation or
custom pressure-boundary physics changes have been made. The accepted conductivity
and boundary-cloning increments are recorded in separate local commits.

## 1. Purpose, priorities, and review agreement

HTFoam simulates **single-phase thermal convection in porous media**, principally
in **submarine hydrothermal systems**, on **OpenFOAM Foundation 10**. It couples
Darcy flow and temperature using p–T-dependent fluid properties from xThermo.
It is not a momentum-equation/Navier–Stokes solver, a salt-transport solver, or a
multiphase-flow implementation. Whether all intended single-phase regimes are
correctly represented is part of the review.

The user's priorities are:

1. Integrate the installed new xThermo while retaining the old installation and
   executable for comparison. Build integration and the minimal fail-fast property
   handling increment are implemented, tested and committed for review.
2. Review boundary conditions, especially inconsistent property sources between
   the solver and custom heat-flux boundary condition.
3. Continue with validation, formulation, initialization/coupling, numerics,
   material interfaces, time stepping, and tutorial migration in small increments.

The user explicitly requires **review and acceptance of every code change**, with
clear stop points. Approval to implement a defined increment is not acceptance of
its results, nor permission to move to the next increment. The user previously
corrected an attempt to create a branch during document-only planning. Subsequently,
the user explicitly authorized the build integration and property-handling
increments, the first three commits and their review-branch push. The user has
subsequently accepted conductivity and boundary cloning and authorized two separate
local commits. No further push, merge, rebase or implementation is authorized.

- Present a concrete scope and affected files before new implementation.
- After an authorized increment, present the diff, tests, results, and limitations;
  stop for acceptance before continuing.
- Do not infer acceptance from a status question such as “what's next?”.
- Do not commit, merge, push, or publish without authorization.
- Do not silently change numerics, property handling, and build plumbing together.
- Preserve the existing solver and saved baseline. Work on the review branch.
- Use `HTFoam-review` until the final merge review; keep `HTFoam` available to users.
- The OpenFOAM-version upgrade and physical-model extensions are separate decisions.
- Reading/gathering information in the local xThermo repository is authorized;
  changing xThermo is not part of the HTFoam work authorized so far.

The concise working plan is [Modernization.md](Modernization.md). This handoff is
the detailed background. Neither supersedes later instructions from the user.

## 2. Current workspace state

History and conductivity status updated on 2026-10-29:

| Item | State |
| --- | --- |
| Repository | `/Users/lruepke/git-geomar/HydrothermalFoam` |
| Branch | `review/htfoam-modernization` |
| Starting HEAD | `695c721b13d1539f3e456faf14582c035c550446` |
| Shared starting branch | `OpenFOAM-10-main` (the user also refers to “master”) |
| Build-only commit | `effec70f` — four build files; output `HTFoam-review` |
| Property/test commit | `7bb71dd1` — five solver files, isolated tests, input-only h1 copy, fixtures and narrow ignores |
| Original documentation commit | `e244ea92` |
| Coupling/timestep/pressure BC physics | Unchanged; conductivity fields and BC cloning API are modernized |
| Acceptance | Conductivity and cloning changes accepted; broad scientific validation remains incomplete |
| Remote | `origin`: private development repository (URL omitted from public documentation) |
| Publication | Three commits through e244ea92 pushed to origin with upstream; no merge |
| Conductivity commit | `e43f420c` — reference/effective fields and consistent heat flux |
| Cloning commit | Separate local fix for all four shared BCs; inspect git log for its hash |

Planning/background/case documents are now included in the documentation increment.
Full `h1-review/baseline-old/`, `review-new/`, solver build trees and test `run-*/`
directories remain ignored, local and preserved. Existing h1/h2 `results.png` are
untracked and deliberately excluded. No repository `AGENTS.md` files were found;
recheck instructions and actual Git state when resuming.

**Transfer:** a checkout includes source, input templates and compact test fixtures,
not full run artifacts or executables. The default test runner needs no local old
baseline. For historical logs/plots/binaries or optional byte comparisons, transfer
the saved directories separately and verify checksums. Compiled macOS binaries and
local absolute paths are not portable. All 1264 files in the commit-preparation
preservation manifest were verified unchanged after verification runs.

## 3. Source map and field meanings

The active executable compiles `solvers/HTFoam/HTFoam.C`. Its included headers form
one translation unit; several communicate through variables declared in the main
program. Historical files are not necessarily active implementations.

| File in `solvers/HTFoam/` | Role |
| --- | --- |
| `HTFoam.C` | Startup, initialization, time loop, fixed p–T Picard loop |
| `createFields.H` | Read p/T/permeability/U; create property fields, gravity, mass flux, models/constraints |
| `readTransportProperties.H` | Read transport dictionary, porosity, rock density/heat capacity |
| `createConductivity.H`, `updateConductivity.H` | Reference kr input, derived kr_eff, boundary communication and validation |
| `createxThermo.H` | Read fluid/backend/composition and instantiate xThermo |
| `updateProps.H` | Evaluate cells/physical faces, communicate coupled properties, check corrected values |
| `evaluateFluidState.H` | Shared input/status/phase/property validation and contextual fatal diagnostics |
| `initpEqn.H` | Active initial pressure/property iteration |
| `pEqn.H` | Transient pressure equation, face mass flux, Darcy velocity |
| `TEqn.H` | Temperature equation |
| `porousCourantNo.H` | Inactive alternative Courant calculation; requires review |
| `releasexThermo.H` | Manual deletion of the thermodynamic object |
| `Make/`, `CMakeLists.txt`, `cmake/` | wmake and local CMake builds |

`HTFoam_backup.C`, `initpEqn_orig.H`, `initpEqn_lhr.H`, and `steam.H` are historical
or alternative material. The active main file includes `initpEqn.H`; do not modify
an unused version and assume the solver changed. The local README describes an
older freesteam-based solver and is not a reliable description of current behavior.

| Code name | Meaning and SI units |
| --- | --- |
| `p` | Thermodynamic pressure supplied to EOS, Pa; not a kinematic pressure |
| `T` | Temperature, K |
| `U` | Darcy/superficial velocity, m/s; pore velocity would be `U/porosity` |
| `phi` | Integrated face mass flux, kg/s; **not porosity** |
| `permeability` | Scalar spatial field, m² |
| `rho`, `mu`, `Cp` | Fluid density kg/m³, dynamic viscosity Pa s, specific heat J/(kg K) |
| `alphaP` | Isobaric expansivity, `-(1/rho) d(rho)/dT` at fixed p, 1/K |
| `betaT` | Isothermal compressibility, `(1/rho) d(rho)/dp` at fixed T, 1/Pa |
| `porosity` | Uniform dimensioned scalar, dimensionless |
| `kr`, `kr_eff` | Reference/derived bulk conductivity fields, W/(m K); reference input defaults to legacy uniform scalar |
| `rho_rock`, `cp_rock` | Uniform rock density and specific heat |
| `constX` | Fixed salinity, kg NaCl/kg fluid; no composition-transport equation |

p, T, and permeability are required case fields. U is read if present, otherwise
starts at zero. Fluid properties are regenerated, not read from restart outputs.
`compressibleCreatePhi.H` reads `phi` if present, otherwise constructs it from
interpolated `rho*U`. `rho` and `mu` are written; Cp/alphaP/betaT are not normally
written. Rock properties come from `constant/transportProperties`; xThermo settings
come from `constant/xThermoProperties`.

## 4. Physical formulation and actual numerical structure

### Intended continuum interpretation

Use epsilon for porosity below, avoiding the code's `phi` mass-flux name.
The following equations explain the implementation; they are **not a completed
independent derivation or proof of conservation**.

Darcy velocity is conceptually

```text
U = -(k/mu) (grad(p) - rho*g)
```

For rigid media and fixed composition, mass conservation motivates

```text
epsilon * rho * (betaT * dp/dt - alphaP * dT/dt) + div(rho*U) = mass source
```

The solver uses the EOS derivative expansion rather than directly discretizing
`ddt(epsilon*rho)`. Equivalence at the continuous level does not guarantee exact
discrete mass balance when properties vary or coupling is not converged.

The temperature equation implemented is schematically

```text
Cbulk * dT/dt + div(rho*Cp*U*T)
  = div(kr*grad(T)) + T*div(rho*Cp*U)
    + (mu/k)*|U|^2
    + alphaP*T*(epsilon*dp/dt + U dot grad(p))

Cbulk = epsilon*rho*Cp + (1-epsilon)*rho_rock*cp_rock
```

Its product-rule correction is implemented implicitly with `fvm::Sp`, as is its
pressure-work term. This is a temperature formulation, not an enthalpy solve.
The continuum energy equation is provisionally accepted following the Phase 0.1
review. Discrete budgets and variable-property convergence still need verification;
this is not authorization to change the formulation. Some equation comments use
porosity symbols differently from code; inspect executable expressions.

### Pressure discretization

`pEqn.H` forms cell mobility `rAU = permeability/mu`, then explicitly interpolates
`rho*rAU` into face coefficient `rhorAUf`. Gravity flux is
`phig = (interpolate(rho)*rhorAUf*g) & Sf`. It calls `constrainPressure` before
assembling pressure solves.

Storage is implicit in p and explicit in T:

```cpp
porosity*rho*betaT*fvm::ddt(p)
- porosity*rho*alphaP*fvc::ddt(T)
+ fvc::div(phiHbyA)
- fvm::laplacian(rhorAUf, p)
== porosity*betaT*rho*fvModels.source(p)
```

The non-orthogonal loop runs from zero through the configured count inclusive.
Each matrix is constrained and relaxed, then solved using the `p` entry. On its
last pass, `phi = phiHbyA + pEqn.flux()` and U is reconstructed using face fluxes
and mobility; U boundary conditions and constraints are then applied. The
`p_rghDDtEqn` variable name does not mean that p is actually a p_rgh field.

### Temperature discretization

`TEqn.H` uses bulk storage times `fvm::ddt(T)`, face mass flux times interpolated
Cp in `fvm::div`, `fvm::laplacian(kr_eff,T,"laplacian(kr,T)")`, and the corrections/heating terms above.
It constrains/relaxes the matrix, solves the `T` entry, then constrains T and
corrects its boundaries. A temperature `fvModels.source(T)` call is commented out.
Source/constraint support and units should be reviewed explicitly.

### Execution order

1. Create time/mesh/control/fields/property object. Conductivity precedes T;
   heat-flux T patches are evaluated before the initial boundary EOS properties.
2. If the time-name string is exactly `"0"`, run initial pressure iteration.
3. Read custom coupling count and non-orthogonal count before the time loop.
4. Each step: read time controls, calculate compressible Courant number, set dt,
   advance time.
5. For each fixed Picard pass: solve pressure and update phi/U; refresh conductivity
   and temperature boundaries, then solve temperature;
   update properties; correct fvModels; print max changes; update snapshots.
6. Write fields and timings. Finally delete the xThermo object.

The transient main loop does not use `pimple.loop()` as a standard PIMPLE outer
loop; PIMPLE settings do not all have their usual solver-wide meaning here.
`pimpleControl` is actively used in initialization.

## 5. Confirmed issues and review questions

### Initialization and coupling

These numerical controls are unchanged by the property increment. One-pass thermal
expansion (F1) is a secondary time-level/coupling question, not a confirmed defect;
assess time refinement before drawing that conclusion. Flux reconstruction also
requires targeted verification rather than rejection of standard OpenFOAM operators.

- `initpEqn.H` explicitly exits when `physOK` alone is true. It computes/prints
  `absOK` and `relOK` but does not combine them with that exit. PIMPLE's own stopping
  must also be considered; do not claim all residual control is absent.
- Physical change threshold is `PTCOUPLING.maxDeltaP`, default `GREAT`. That default
  is effectively permissive. Comments/messages refer to `INIT.maxDeltaP` instead.
- h1/h2 specify `maxInitOuterIters=200`, which is never read. Their
  `PIMPLE.nOuterCorrectors=1` bounds the current initialization.
- Actual h1 runs continued after `physOK=0` and a pressure change of about
  24.96 MPa; an existing h2 log showed about 20 MPa. These are recorded failures
  of the physical change criterion, not reasons to bless current initialization.
- Despite the “hydrostatic” name, zero-gravity h1 initialization solves a
  boundary-driven steady pressure equation and produces pressure-driven flow.
- Initialization assembles coefficients before its inner correctors, while
  updating properties inside them. Review when updated properties enter matrices.
- `tightCouplingIters=0` means one pass; positive values mean the **total** pass
  count, not that many additional passes. There is no transient nonlinear stopping
  test or rejection policy.
- Recorded residual variables and final-temperature flags do not currently select
  `pFinal`/`TFinal` or govern transient convergence.
- Final property updates leave phi/U based on the preceding pressure solve's
  properties. Quantify acceptable end-state inconsistency or converge it away.
- Review old-time storage, equation relaxation, runtime control rereading,
  fresh/restart behavior, and pressure references for closed/all-Neumann cases.

### Conservation, material interfaces, and time stepping

- Continuity diagnostics are commented out; no validated mass/energy budgets
  have been established. A small linear residual does not prove conservation.
- Permeability and conductivity can now be fields; rock heat-storage properties
  and porosity remain uniform scalars. Layered isotropic conduction is covered;
  broader material/mesh validation remains outstanding.
- Review interpolation of combined `rho*k/mu` versus separation of material
  resistance and fluid properties. Test harmonic/distance-weighted and arithmetic
  choices against layered analytical cases; do not prescribe one mean universally.
- The active OpenFOAM compressible Courant calculation divides mass flux sums by
  density and cell volume, not porosity. It measures a Darcy-based transport rate.
  Pore advection and effective thermal propagation have different storage scales.
- Inactive `porousCourantNo.H` divides mass flux by volume without density or
  porosity conversion. Simply enabling it is not a correct pore Courant fix.
- Assess time-step accuracy as well as stability and property/nonlinear limits;
  Euler versus higher-order schemes needs convergence studies, including restarts.
- Tensor permeability, variable rock fields, and an enthalpy formulation are scope
  decisions, not already approved deliverables.

## 6. Boundary conditions: second priority

Custom code lives in `libraries/BoundaryConditions/`, built as
`libHydrothermalBoundaryConditions`. This shared library is used beyond the solver;
future test builds must also avoid unintentionally replacing other users' library.
The conductivity increment changes HydrothermalHeatFlux. A separate clone-API fix
changes all four shared BC headers without changing their pressure/flux formulas
or .C implementations. Shared libraries are built only in isolated test directories.

### Conductivity increment (accepted and committed locally)

`krSource uniform` (default) reads the legacy scalar; `krSource field` requires the
reference kr volume field at the selected start time and writes it for restart.
Registered kr_eff is derived, validated and never read back as restart input.
Physical derived values are explicitly copied from corrected reference patches;
standard constraint patches communicate coupled values. The shared heat-flux BC
uses this field only with explicit `conductivityField kr_eff`, otherwise retaining
its legacy dictionary lookup. Startup creates conductivity before T and evaluates
heat-flux T faces before boundary EOS. Pre-assembly refresh holds one coefficient
snapshot for T boundary evaluation and matrix assembly; no new law/multiplier exists.
The explicit Laplacian lookup name remains laplacian(kr,T), preserving old schemes.

Isolated builds and 22 serial/4 MPI/1 cyclic checks passed; h1 retains byte-identical
profile and six principal fields at saved precision. Layered tests use harmonic
interpolation with unequal cell widths, including a processor interface at the
material jump. Restart tests reconstruct stale derived output and corrupted saved
heat-flux values/gradients. See [conductivity tests](tests/conductivity/README.md) for
input examples, commands, analytical reference, numerical results and limits.
Existing tutorials and other solver configurations were not migrated. The user
accepted this increment and authorized local commits; no further push or merge is
authorized. Boundary clone corrections are recorded separately.

### Boundary cloning correction (accepted and committed separately)

All four BC headers delete the unsupported plain constructor and remove no-argument
clone(), preserving the explicit-internal-field constructor and clone(iF). The
previously unresolved constructor symbols are gone. Strict Linux ARM64 linking of
the complete library and both probe clients passes without permissive flags; ldd -r
reports no unresolved dependencies. Fifteen checks pass on each of macOS and Linux,
covering negative compilation, supported construction/cloning, values/configuration
and owner references. All 27 conductivity regressions pass after the full rebuild.
See [boundary cloning tests](tests/boundaryClones/README.md) and the focused
[HeatFlux contract checks](tests/heatFluxClone/README.md). This does not establish
correctness of unrelated pressure-BC serialization or dynamic-mesh mapping paths.

### Historical conductivity-source mismatch

Before the current increment, HTFoam read scalar `kr` from transportProperties.
The BC legacy mode still looks up a registered
`thermophysicalProperties` dictionary, then `mixture/porousMedia/kr`, and computes
`gradient() = q/kr` (also for its spatially varying flux shapes).

Consequences to investigate:

- If the registered dictionary is missing, lookup may fail. Merely having a file
  on disk is not proof that the object is registered in the mesh database.
- If the boundary and equation conductivities differ, the equation's conductive
  flux magnitude is scaled by `kr_solver/kr_boundary` relative to the boundary's
  intended flux, assuming the same gradient/sign convention. For 2 versus 1.5,
  the factor is 4/3. This is an algebraic implication, not a measured h1 heat-flux
  error; normal orientation/sign must be checked in a targeted test.
- Copying dictionary values until they match would hide the duplicate source.
  Propose a shared authoritative source and a compatibility/migration policy.

h1 actually has `kr=2` and `rho_rock=2700` in `transportProperties`, versus
`kr=1.5` and `rho_rock=3000` in legacy `thermophysicalProperties`. Its T boundaries
are fixed values, so it **does not invoke HydrothermalHeatFlux** and cannot validate
or quantify that BC mismatch. A comprehensive inventory of affected maintained
tutorials has not yet been performed.

### Other boundary interactions

| Condition | Current implementation to audit |
| --- | --- |
| `noFlux` | Pressure gradient `phig/(rhorAUf*magSf)`; depends on solver-created face fields |
| `HydrothermalMassFluxPressure` | Gradient `(phig-q)/(rhorAUf*magSf)`; establish whether q is integrated face flow and check units/signs |
| `submarinePressure` | Fixed pressure `0.1e6 + rhoValue*(g dot Cf)`, default density 1013; verify coordinate/datum convention and restart serialization |
| `HydrothermalHeatFlux` | Legacy conductivity source, prescribed/spatial heat-flux shapes, gradient sign and physical flux |

These are audit targets, not assertions that every condition is incorrect.
For example, a fixed external seawater density in submarine pressure can be an
intentional boundary model rather than the interior EOS density.

### Property boundary handling: implemented and reviewed

The old `isA<processorPolyPatch>(fvPatch)` hierarchy mismatch is corrected. The
current update evaluates the EOS for cells and noncoupled physical faces, skips
empty/coupled faces, assigns updated internal fields, then calls standard property
boundary correction in identical order on every rank. It checks all resulting
active boundary property values. Field-copy allocation is retained.

Physical property patches are normally `calculated`; their correction does not
compute EOS values from p/T. Removing face evaluation would leave stale values or
replace physical boundary states with extrapolated cell values and can change
mobility/conduction-advection coefficients and boundary fluxes. Fixed-value p/T
therefore need EOS evaluation at their actual face state; zero-gradient p/T give
the adjacent-cell state when current. Explicit field patch types, if changed in
future, must be examined for their own correction behavior.

Processor patches exchange neighbour property values; cyclic correction/interpolation
uses coupled neighbour data. This is standard field communication, not EOS evaluation
at an interpolated p/T. It retains the finite-volume interpolation of properties.
Empty patches have no active values. Two-rank/nonuniform and cyclic checks passed,
but do not establish every coupled geometry or prove the cause of old parallel
problems. The old comment described its cause as a guess. No custom BC was modified.

### Processor-boundary input audit (2026-11-02)

The local Foundation 10 `decomposePar/fvFieldDecomposerDecomposeFields.C:54`
uses `owner[-addressing[i] + 1]` in `mapCellToFace`. A signed one-based face
address `a=-(f+1)` requires `owner[-a-1]`; the installed expression selects
`owner[f+2]`. The [original published Foundation 10 source](https://cpp.openfoam.org/v10/fvFieldDecomposerDecomposeFields_8C_source.html)
has this defect; [Foundation 11](https://cpp.openfoam.org/v11/fvFieldDecomposerDecomposeFields_8C_source.html)
and the [current Foundation 10 master](https://raw.githubusercontent.com/OpenFOAM/OpenFOAM-10/master/applications/utilities/parallelProcessing/decomposePar/fvFieldDecomposerDecomposeFields.C)
use `-1`. This confirms an installed-revision defect, not a claim about every
Foundation 10 installation. The demonstrated path constructs volume-field
processor patches on negative addresses; surface-field mapping is separate.

Internal cells use independent `cellAddressing_`, so they can remain correct
while stored neighbour values are wrong. The preserved unique-cell-ID check
found all 90 negative-address ghosts wrong, including two permeability ghosts
assigned the wrong layer. Reading a processor patch does not exchange values;
`patchNeighbourField()` returns its stored array. In `createFields.H:64`,
`permeability.correctBoundaryConditions()` initiates and completes coupled
exchange from the actual remote internal cells before either pressure path
constructs mobility. It runs on startup and restart; physical cell values remain
unchanged. No external OpenFOAM source or executable was patched.

The isolated permeability-fix regression used ten one-year steps from both zero
and 5000 years, with two/four ranks crossing the material interface and plume.
Before correction, restart pressure RMS/max differences were 522/4053 Pa,
net interface flow was 14.91% low, and opposing processor fluxes differed by
up to 1.05e-5 kg/s. After correction, pressure maxima were below 0.232 Pa,
temperature maxima below 4.42e-7 K, and processor flux cancellation error below
5.56e-17 kg/s, without manual file edits. Serial results were unchanged.
Evidence remains outside Git in `../HTFoam-permeability-mpi-fix-20261102/`
and `../HTFoam-layered-mpi-20261102/` (relative to the repository root).

Conductivity already corrects `kr`, copies physical values/internal cells to
`kr_eff`, then corrects `kr_eff` before T construction and each assembly, also
on restart. EOS properties are rebuilt and communicated rather than read.
Rock storage, porosity and salinity inputs are uniform scalars.

Maintained case preparation supplies neither `U` nor `phi`: U defaults to zero,
and `compressibleCreatePhi.H` initially constructs zero phi from `rho*U`.
Pressure initialization establishes Darcy flux before the first Courant check
for h1-h3 and both 2D cases. v1-v3 deliberately disable initialization; their
first transient pressure solve establishes the flux. Normal saved-state restarts
read written phi. A missing-phi restart with spatial input U remains an unverified
edge case: its stored processor values are not explicitly synchronized before
fallback flux construction, but no impact on the supported workflow has been
demonstrated. No U synchronization change is justified by this audit. Other
coupled geometries, long-time MPI equivalence and EOS mass conservation remain
outside these short tests.

## 7. xThermo: installation, API, and scientific expectations

### Available installations and documentation

Source is `$HOME/git-geomar/xThermo` (also referred to as lowercase `xthermo` in the
conversation). The user authorized reading/gathering information there.

| Installation | Purpose/layout |
| --- | --- |
| `install/` | Old fallback; old HTFoam linked against the older layout |
| `install-master/` | New installation used in the review build |
| `build-master/` | User's build tree; observed Release, bundled GSL on, Python on, OpenMP off |

Do not install the new layout over `install/`. Bundled GSL is pinned to **2.8**,
downloaded from GNU with checksum verification; the old `gsl-2-7.tar.gz` is not the
correct pinned archive. The supplied example used `XTHERMO_PYTHON=OFF`, but the
actual observed cache has Python enabled; C++ integration does not require disabling it.

New installed paths:

```text
include/xThermo/thermo.h
include/xThermo/H2ONaCl.h
lib/libxThermal.a
lib/xThermo/gsl/include/
lib/xThermo/gsl/lib/libgsl.a
lib/xThermo/gsl/lib/libgslcblas.a
lib/cmake/xThermo/xThermoConfig.cmake
```

The source checkout recorded during the successful review run was
`e229848e0a98bb7e3d630549ddef91dd04c824a7`. This does **not** independently prove the
revision used to build the installed archive. Build logs record actual linked paths;
archive and executable hashes are preserved in the run provenance.

Read xThermo's `review/OUTSTANDING_DEFECTS.md`, `review/PROJECT_CONTEXT.md`,
`review/MODEL_SPECIFICATION.md`, and relevant batch reports before interpreting
changes. Distinguish committed fixes, remaining defects, and documented scientific
limitations. Header contracts are available in installed `thermo.h`, `Exception.h`,
and `DataStructures.h`.

### API and state checks

The previous throwing API remains available in xThermo:

```cpp
props = pxThermo->UpdateState_TPX(T, p, constX);
```

The current guarded implementation uses:

```cpp
xThermal::EvaluationStatus status =
    pxThermo->tryUpdateState_TPX(props, T, p, constX, &message);
```

The latter catches xThermo evaluation errors and maps them to `Ok`, `InvalidInput`,
`OutOfRange`, `NotConverged`, `NotAvailable`, or `Failed`. On evaluation failure,
inputs are retained but result values are invalidated to NaN and phase Unknown.
Unrelated exceptions, such as allocation failures, can still propagate.

Successful evaluation is not proof of a usable HTFoam state:

- A required transport property can be NaN even when state evaluation succeeds.
- Multiphase bulk property conventions are not a single-phase flow model.
- Validate supported fluid phases, composition, finite values, and required
  properties. Do not impose a blanket positive-expansivity check.
- xThermo documents a stable-brine negative-compressibility limitation in a
  low-pressure/high-salinity region; do not silently alter its correlation.
  Decide how HTFoam restricts unsupported/problematic states.
- One thermodynamic object is not thread-safe. Independent objects are needed per
  external evaluation thread. MPI ranks already have separate address spaces;
  do not add threading without a reviewed design.

Current policy in `evaluateFluidState.H` and `createxThermo.H`:

- Require finite positive T/p and X in [0,1], then retain advertised model bounds.
- Translate non-Ok evaluation status and standard exceptions into fatal OpenFOAM
  errors with backend, p/T/X, stage, time/rank and cell or patch/face/centre context.
  Configuration failures occur before p/T fields are read and report that context.
- Allow `SinglePhase_L`, `SinglePhase_V`, `Supercritical`, `Supercritical_vapor`,
  `Supercritical_liquid`; reject exact Critical, solid, multiphase and Unknown.
- Require finite positive rho/mu/Cp/betaT; require only finite alphaP. Real cold-water
  negative alpha is accepted. Real low-pressure brine negative beta is rejected,
  with no correction to xThermo's correlation.
- No clipping, fallback state, rollback or automatic retry. Default missing constX=0
  is retained. Pure-water CoolProp stays disabled; diagnostics no longer advertise
  it as supported. No backend or envelope was expanded.

Startup constructs dimensioned zero-valued storage, then fills it from actual p/T
before gravity/flux construction or equation use. The dummy 278.15 K / 1 MPa EOS
state and initial Mu_l selection were removed; all updates use state.Mu. Zero
storage is not a fallback property state. Initial p/T boundary ordering and
physical-face evaluation were retained. Coupled patches communicate properties;
phase is validated at evaluated source states but is not communicated as a field.

Finite output and phase checks cannot detect all thermodynamic inaccuracies.
Documented xThermo defects, derivative accuracy, critical proximity and correlation
limits still apply. The installed API/status/enumeration contract is now required;
this property increment is not compatible with older xThermo headers lacking it.

### Expected changes in numerical results

Density-derivative corrections affected parts of the range by approximately
9–53%, with additional IAPWS95 and stale-state corrections. Since HTFoam uses
expansivity/compressibility, differences may be correct and should be traced to
the library's scientific/correction reports. Conversely, do not excuse every new
difference as a correction without evidence.

Invalid evaluations now throw instead of silently returning zeros or previous
states. For example, brine above the 1000 °C model limit raises `OutOfRangeError`;
that is not a universal bound for all pure-water backends. Removed debug prints
are gone, though some warnings can still occur.

## 8. Build integration completed so far

OpenFOAM activation must use **bash**:

```bash
source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc
```

New shell-local setting:

```bash
export xThermo_DIR=$HOME/git-geomar/xThermo/install-master
```

Do not edit `~/.zshrc`. The xThermo library is static, so switching installations
requires rebuilding the executable; changing the environment does not relink an
already-built program.

Completed changes:

- wmake outputs `$(FOAM_USER_APPBIN)/HTFoam-review`; xThermo/GSL include and link
  paths use the new layout.
- CMake links exported `xThermo::xThermal` and outputs `HTFoam-review`.
- The helper uses `HTFOAM_XTHERMO_ROOT` for an installation prefix. CMake's own
  `xThermo_DIR` cache value means the package-config directory. Use a fresh build
  directory when migrating from the old helper/cache.
- Existing OpenFOAM build configuration is otherwise retained; wmake used the
  optimized platform settings, while the local CMake helper has its existing
  debug/FULLDEBUG configuration. Do not infer performance differences from the
  two builds or the short historical run timings.
- Both builds passed (58 wmake and 59 CMake warnings retained in logs). Those
  warnings have not been individually resolved or classified as harmless.
- h1 was run with the wmake executable. The property increment also passed a fresh
  CMake build and hot-brine startup/time-loop smoke; no full CMake h1 run was done.

Actual workspace output locations:

```text
benchmarks/HydrothermalSinglePhaseDarcyFoam/HydrothermalFoam/1d/h1-review/review-new/bin/HTFoam-review
solvers/HTFoam/build-review/HTFoam-review
```

The old user-installed executable is still at:

```text
/Users/lruepke/OpenFOAM/lruepke-10/platforms/darwin64ClangDPInt32Opt/bin/HTFoam
```

A review build used a shell-local `FOAM_USER_APPBIN` inside the workspace, preserving
that old installed executable. For future commands, verify the selected binary
with `command -v` or use its explicit path; the review binary is not automatically
on the default PATH.

## 9. h1 baseline and new-run evidence

Migration note: tracked benchmark inputs, tools and documents now live under
`benchmarks/HTFoam/`. Historical executable, baseline and result locations in
this section remain under `benchmarks/HydrothermalSinglePhaseDarcyFoam/`; they
were not relocated or rewritten. Use the new root for maintained source files.

Let `R` mean:

```text
benchmarks/HydrothermalSinglePhaseDarcyFoam/HydrothermalFoam/1d/h1-review/
```

| Path under R | Contents |
| --- | --- |
| `README.md` | Case review and baseline notes |
| `BUILD_REVIEW.md` | Historical build-only evidence, commit and later-status notes |
| `temperature/` | Input-only copied case; application now `HTFoam-review` |
| `compare_hydrotherm.py` | Validated comparison/overlay script |
| `baseline-old/bin/HTFoam` | Snapshot of existing old executable |
| `baseline-old/case/` | Old inputs, mesh, logs, final fields, profiles |
| `baseline-old/comparison/` | Old-vs-HYDROTHERM PNG/PDF/JSON |
| `baseline-old/provenance.json`, `SHA256SUMS` | Executable/input/reference metadata and integrity manifest |
| `baseline-old/environment.txt`, `dynamic-libraries.txt`, `commands.txt` | Environment, linkage and run details |
| `review-new/bin/`, `review-new/case/` | New executable and separate run |
| `review-new/comparison/` | Three-series plots and metrics |
| `review-new/log.wmake`, `log.cmake-configure`, `log.cmake-build` | Build evidence |
| `review-new/provenance.json`, `solver-build.diff` | New checksums and build-file diff snapshot |

**Never run cleanup or overwrite files in `baseline-old/case`.** The copied
`run.sh` invokes `clean.sh` before running, so it is inappropriate for preserved
results. Keep new experiments in separately named case/output directories. The
baseline is not an assertion that the old behavior is scientifically correct.

### Case definition

- Horizontal length 2000 m, 200 × 1 × 1 cells, scalar permeability 1e-15 m².
- Gravity zero; fixed p left/right 50/25 MPa, fixed T left/right 350/150 °C.
- Initial p 25 MPa, T 150 °C. Other boundaries empty.
- H2O–NaCl/IAPS84, `constX=0` (zero salinity).
- Porosity 0.1; active conductivity 2 W/(m K), rock density 2700 kg/m³,
  rock specific heat 880 J/(kg K), consistent with HYDROTHERM input rock values.
- Euler time stepping and upwind thermal advection. Fixed dt 864000 s (10 days).
- End time 7884000000 s = 250 × 365 days = 9125 steps; final field precision 6.
- 1000 line-sample points; reference has 200 cell centres spanning 5–1995 m.
- `nOuterCorrectors=1`, `nNonOrthogonalCorrectors=1`, `tightCouplingIters=0`.
- `maxInitOuterIters=200` is present but unused. `0/h` is a retained unused field.
- Loads the custom BC library despite using fixed-value/empty conditions.

This is pressure-driven thermal transport, **not a buoyant plume or custom
heat-flux BC test**. Do not call it sufficient validation of submarine convection.

### Measured outcomes

Both old and new runs completed normally at 250 years. Old run reported about
9 seconds; new about 5 seconds (not a controlled performance comparison).
Both continued after initialization reported `physOK=0`.

| Comparison against HYDROTHERM | RMSE | Maximum absolute error |
| --- | --- | --- |
| Old temperature | 3.2828764815 °C | 12.5710074925 °C |
| New temperature | 3.2828764815 °C | 12.5710074925 °C |
| Old pressure | 0.1554784407 MPa | 0.2417833666 MPa |
| New pressure | 0.1554784407 MPa | 0.2417833666 MPa |

The final sampled x/T/p file is byte-identical old versus new at saved precision;
new-minus-old metrics on the reference grid are zero. This does not establish
bitwise equality of internal full-precision states or validate corrected brine
derivatives at nonzero salinity. Scientific acceptance tolerances remain unset.

Old executable SHA256:
`79a704391f2703924c9b2595d9184f15372626bfe3dbbbd8e7a4c7d0a80e132a`.
Historical build-only wmake executable SHA256 (not the property-increment binary):
`9267aa6008d3fc447378247e8d6805376672b5a0873f6de469f0792d5ce6fb29`.
New xThermo archive SHA256:
`139d1e078b5cb762614e10cb7dcf61ed4a674f56407beb8bbdcc015b840a8245`.
The old executable's exact build revisions are unknown; hashing the current old
archive does not prove what was originally linked into it. All old baseline
manifest files and the original installed executable were checked unchanged at
completion of the build increment and again during commit preparation. Reverify
on resumption.

## 10. Reproduction and comparison commands

The following commands document workflows, not permission to rerun/overwrite saved
artifacts. Choose fresh output directories for new experiments.

Build from the repository root in bash:

```bash
source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc
export xThermo_DIR=$HOME/git-geomar/xThermo/install-master
# For a future build, choose a fresh workspace-local executable directory:
export FOAM_USER_APPBIN="$PWD/solvers/HTFoam/tests/propertyHandling/run-NEW/bin"
mkdir -p "$FOAM_USER_APPBIN"
(cd solvers/HTFoam && wmake)
cmake -S solvers/HTFoam -B "$FOAM_USER_APPBIN/../cmake"
cmake --build "$FOAM_USER_APPBIN/../cmake" -j2
```

Do not replace an existing executable artifact needed for reproducibility.
The existing wmake binary and CMake binary already reside at the paths above;
rebuilding them is unnecessary merely to inspect the result.

The completed xThermo installation sanity check was:

```bash
"$xThermo_DIR/bin/xThermal" thermo -D0 -VPTX -T300 -P300E5 -X0.1
```

Expected Liquid and Rho approximately 849.034 kg/m³. **CLI** T is °C and P is Pa
(the output shows 300 bar); **C++ API** temperature is K. Do not feed 300 K to the
C++ API and expect the CLI's 300 °C reference result.

The separate h1 run used `blockMesh`, then an explicit relative executable path,
with logs redirected inside its new case. The same numerical case inputs were
used old/new except for `application`; tracked copies later had only trailing
whitespace normalized. It was a full run, not a one-step smoke test.

To regenerate an overlay without rerunning the solver, from R:

```bash
python3 /path/to/repository/benchmarks/HTFoam/postprocess/one_d/compare_h1.py \
  --sample review-new/case/postProcessing/linesample/7884000000/data.xy \
  --baseline baseline-old/case/postProcessing/linesample/7884000000/data.xy \
  --label 'HTFoam-review / xThermo master' \
  --output-dir comparison-inspection
```

Requires NumPy and Matplotlib. The default system/homebrew Python initially lacked
Matplotlib; dependencies were prepared in an isolated uv environment without
changing project dependencies. The equivalent available workflow is
`uv run --offline --no-project --with matplotlib --with numpy python ...`, subject
to local cache availability/permissions. Preserve a working environment rather
than assuming every `python3` has the dependencies.

Script behavior:

- Resolves reference relative to the script, so working directory does not control
  reference discovery. Reference remains in the shared repository tree, not copied.
- Uses `USGS_HYDROTHERMAL/1d/h1/h1_T_p_250.0.txt` under the benchmark family.
- Solver columns m/K/Pa; reference m/°C/bar. Converts temperatures to °C and p to MPa.
- Accepts `data.xy` or `data_T_p.xy` when auto-discovering; ambiguity is an error.
- Requires reference time 7884000000 s, finite strictly ordered profiles, three
  columns and coverage of all reference centres. An explicit file's actual time
  still needs provenance; the script cannot infer time from arbitrary file contents.
- Interpolates each solver profile onto reference centres, avoiding endpoint
  extrapolation. Metrics are unweighted RMSE and maximum absolute difference.
- Optional baseline gives old-vs-reference and new-minus-old metrics on that grid.
- Writes headless PNG/PDF/JSON; does not launch a viewer or silently accept absent
  references. Exit success means valid comparison data, not passing error limits.

Synthetic reference-equivalent data tests checked conversions, rendering, missing
data, wrong time, NaNs, and incomplete coverage. Real old/new plots were also
rendered and visually inspected. Targeted property tests are now available; broad
scientific/numerical regression coverage remains incomplete.

## 11. Completed property verification and next review scope

Reproduction instructions and exact test limitations are in
[tests/propertyHandling/README.md](tests/propertyHandling/README.md). The runner
requires installed OF10/xThermo and separately built solver/probe binaries, but no
old executable or local h1 snapshot by default. Compact tracked text fixtures store
200-cell p/T/U/rho/mu, 199 internal phi values and the 1000-point profile, with input,
reference and executable provenance/checksums. The old binary's source revision is
unknown; provenance explicitly does not infer it from the source checkout.

Default numeric comparisons use maximum-reference-magnitude scaling with 5e-6
relative tolerance (profile coordinates 1e-12), allowing margin over six-digit
rounding; these are regression limits, not EOS/scientific accuracy criteria.
`--baseline PATH` adds optional byte comparison against all six full final fields
and the profile. Repeatable `--preserve PATH` hashes additional local artifacts.
Neither old/new snapshot is discovered or required implicitly.

Verification completed:

- Both IAPS84 and IAPWS95 brine startup at X=0.1, 573.15 K and 30 MPa agrees with
  direct guarded EOS density to relative tolerance 1e-12.
- Invalid input/domain/backend, real unavailable viscosity, real multiphase and
  negative-beta states fail with context. Physical-face failures identify patch,
  face and centre. Injected statuses/exceptions/NaNs and phase enums test policy.
- Real vapour, supercritical water and negative-alpha liquid water are accepted.
- Cyclic communication and a two-rank nonuniform brine case pass. Serial/parallel
  relative differences are <=4.10e-11 p, 0 T, 1.89e-12 rho, 2.72e-12 mu and
  2.74e-9 U/phi. A rank-1-only invalid state aborts without hanging.
- Property-increment h1 runs all 9125 steps; profile and six final fields are
  byte-identical to the old run at saved precision. No initialization fix is implied.
- An isolated export without full snapshots passed 31 serial and 2 MPI checks.
  A separate optional full-baseline run passed 32 serial checks. Existing tested
  binaries matched unchanged solver source hashes; these were not new rebuilds.

Detailed original evidence remains ignored in `tests/propertyHandling/run-20261029/`;
commit preparation/export evidence is in `run-commit-prep/`. Fixture/input whitespace
and provenance normalization do not change numerical settings. Generated logs,
plots, binaries, full snapshots and build trees are excluded from commits.

**Next task needs a new reviewed scope.** The accepted field-based conductivity
increment and prescribed-flux tests are complete. Remaining boundary work includes
inventorying maintained cases and deciding compatibility/migration policy before
changing their dictionaries. Initialization convergence/failure handling is the
leading remaining solver robustness concern.
Further governing-equation, coupling, timestep or BC-physics changes need separate
review and authorization.
The continuum energy formulation is provisionally accepted; F1 is secondary and
requires evidence before any defect classification. Keep the two-day effort focused
on necessary correctness/robustness work rather than broad refactoring.

Later focused validation should cover:

| Test | What it must establish |
| --- | --- |
| Hydrostatic column, variable density | Correct equilibrium and negligible spurious flow |
| Pressure diffusion | Storage/EOS derivative consistency and convergence |
| Prescribed-flux conduction | Correct boundary energy input and shared conductivity |
| Thermal advection | Speed, diffusion, temporal/spatial convergence |
| Layered permeability/conductivity | Effective resistance and normal flux continuity |
| Nonzero-salinity p–T property tests | Derivative corrections relevant to HTFoam |
| Near-domain/invalid states | Phase/property checks and coordinated failure diagnostics |
| Buoyancy-driven convection/plume | Hydrothermal heat transport and nonlinear robustness |
| Serial/parallel and restart pairs | Communication, accepted-state and history consistency |
| HYDROTHERM cases | Cross-code agreement under documented EOS/physics differences |

For every numerical change, assess mass/energy budgets and distinguish linear,
nonlinear, discretization, EOS, and cross-code errors. Establish justified acceptance
criteria with the user rather than fitting thresholds to current results.

## 12. Tutorials, CI, and things not to assume

Some tutorials retain old thermophysical dictionaries, schemes, settings, or solver
names. A full migration is not complete. Start with one canonical OF10/xThermo case,
then representative BCs/geometries before bulk migration. Preserve useful legacy
compatibility deliberately and document changed settings.

`docker/test-image.sh` provides a one-step HTFoam smoke test. `.gitlab-ci.yml`
currently includes `.gitlab/publish_public.yml`; it publishes public snapshots and
does not run numerical regression tests. Publication is consequential: do not
trigger or alter it merely to test local modernization changes.

Avoid these incorrect conclusions:

- “The property guards certify EOS accuracy or cover every coupled geometry.”
  Build integration and focused guard tests are complete; broad validation is not.
- “Old/new h1 agree, therefore all derivatives and convection are validated.”
- “h1 demonstrates the heat-flux boundary bug”: it does not use that boundary.
- “The baseline is scientifically accepted”: it preserves known issues for comparison.
- “PIMPLE residual settings control all transient nonlinear convergence.”
- “A successful EOS state guarantees finite usable transport properties.”
- “A local commit or permission to commit means scientific acceptance or merge approval.”
- “All artifacts will follow a Git checkout”: many are untracked or ignored.

Resume by checking current instructions, branch/diff, acceptance state, baseline
integrity, and the exact next approved scope. Preserve the user's stepwise review
process throughout.

## Current benchmark entry points

The maintained suite is [benchmarks/HTFoam](../../benchmarks/HTFoam/README.md).
Use its root `run.py`, `postprocess/compare_1d.py`, and `postprocess/plot_2d.py`.
Paths and commands in the earlier sections above are historical records; those
source/tool versions are retained in Git and the verified local source archive.
