# HTFoam conductivity and heat-flux verification

Accepted conductivity increment, 2026-10-29. These tests use a separate library
and executable; no installed binary or preserved baseline is overwritten.

## Input contract

Legacy uniform cases need no change:

```foam
// constant/transportProperties
krSource uniform; // optional; default uniform
kr kr [1 1 -3 -1 0 0 0] 2;
```

For spatial conductivity use `krSource field;` and a required `kr` volume field
at the selected starting time, with dimensions `[1 1 -3 -1 0 0 0]`. This mode ignores
the scalar kr entry if one remains in the dictionary. The field is written at
output times so it is available at restarts. Missing restart kr is fatal. Uniform
mode ignores any kr field files and does not write its reference field.

Both inputs mean bulk conductivity [W/(m K)] as used by the existing equation;
there is no porosity rescaling or new constitutive law. The registered derived
`kr_eff` is written for inspection but **never read as restart input**.

Use physical `zeroGradient` reference patches for continuation of the adjacent
material, or explicit reference patch values when those are physically intended.
Processor/cyclic/empty patches use standard mesh constraints. `kr_eff` stores
explicitly derived physical values on calculated patches and communicates coupled
values after assigning internal cells; it does not clone independent reference BC
objects. Values and dimensions are validated. No clipping/fallback is performed.
Reference conductivity BCs must be independent of T and kr_eff: their startup
correction occurs before T exists. There is no automatic rereading from subsequent
time folders or runtime scalar-dictionary refresh. Existing reference boundary
conditions are reevaluated before each temperature assembly; future internal laws
belong in updateConductivity.H, not in the temperature BC.

For HTFoam heat-flux patches select the derived field explicitly:

```foam
bottom
{
    type hydrothermalHeatFlux;
    conductivityField kr_eff;
    q uniform 20; // positive heat input, W/m2
    value uniform 0;
}
```

Without `conductivityField`, the shared BC retains the registered dictionary lookup
`thermophysicalProperties/mixture/porousMedia/<kr>` used by legacy solvers. There is
no automatic field fallback. All shapes divide by physical patch conductivity
face by face. Positive q gives outward-normal gradient q/k and inward heat input.
Gaussian coordinates are global x (2d) or x/z (3d); their discrete total input is
sum(q_face*area_face). `z0` is now read/written consistently; `z0_` remains an input
alias, with z0 taking precedence. Linear profiles now retain x1/x2/q1/q2 on restart.
Nonuniform prescribed q is mapped with the patch. Invalid conductivity, nonfinite
flux, unknown shape and degenerate Gaussian/linear parameters fail explicitly.

## Ordering and scheme lookup

HTFoam creates valid kr/kr_eff before T. After reading T, it evaluates only
hydrothermalHeatFlux patches before the first boundary EOS evaluation, including
on restart. It does not prematurely evaluate phi-dependent patches such as
inletOutlet. Before each temperature matrix it refreshes conductivity, evaluates
T boundaries, and holds that coefficient snapshot for assembly. The existing
post-solve T correction and EOS update remain in place.

Foundation 10 `fvmLaplacian.C` constructs a default lookup from gamma.name(): simply
changing the coefficient to kr_eff would require `laplacian(kr_eff,T)`. Production
therefore calls `fvm::laplacian(kr_eff,T,"laplacian(kr,T)")`. Existing case schemes
are preserved. Tests use only the explicit old key, with `default none`, proving
that lookup. Volume coefficients are interpolated by the selected Laplacian scheme.
The earlier scalar overload constructed a uniform surface coefficient.

Layer tests deliberately use `laplacian(kr,T) Gauss harmonic corrected;`. Foundation
10 harmonic interpolation uses distance-weighted series resistance, including on
coupled patches. No hand-built face coefficient or global scheme change is added.
This is for isotropic, face-aligned materials; it is not a contact-resistance,
subcell-interface, anisotropy or arbitrary-skew-mesh model.

## Reproduce

From the repository root in **bash**, choose an unused absolute run path:

```bash
source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc
export xThermo_DIR=$HOME/git-geomar/xThermo/install-master
conductivity_run="$PWD/solvers/HTFoam/tests/conductivity/run-NEW"
bash solvers/HTFoam/tests/conductivity/build.sh "$conductivity_run"
ulimit -c 0
python3 solvers/HTFoam/tests/conductivity/run_tests.py --run "$conductivity_run"
python3 solvers/HTFoam/tests/conductivity/run_tests.py --run "$conductivity_run" --cyclic
python3 solvers/HTFoam/tests/conductivity/run_tests.py --run "$conductivity_run" --mpi
```

The build script copies sources and creates all objects/binaries/lnInclude in the
ignored run directory. It refuses to overwrite an existing directory. The runner
requires the isolated library, selects it explicitly in controlDict and prepends
its directory to the dynamic-library search paths (necessary on macOS even for
absolute dlopen paths). MPI requires local sockets. Runs refuse to overwrite their
case directories. Logs, source snapshots and failed attempts are retained locally.

The default h1 check uses tracked propertyHandling fixtures, not a local old binary
or full snapshot. Optionally add `--baseline /path/to/h1-review/baseline-old` to the
serial invocation for byte comparisons of all six final fields and the profile.
Use a fresh run directory for that invocation. No original benchmark is cleaned.
The steady probe also uses the production create/update conductivity headers and
the shared runtime BC; its matrix flux is used for internal-flux verification.

## Analytical reference and results

Column height/area 1 m/1 m2. Bottom y=0, interface y=0.5, top y=1. Inward bottom
flux 20 W/m2, top 300 K, zero gravity, equal pressure boundaries. The bottom/top
blocks have 20/40 cells, so interpolation must account for unequal distances.

| Bottom/top k [W/(m K)] | dT/dy below/above [K/m] | Interface T [K] | Bottom T [K] |
| --- | --- | --- | --- |
| 2 / 4 | -10 / -5 | 302.5 | 307.5 |
| 4 / 2 | -5 / -10 | 305 | 307.5 |

For q=20, T(y)=300+q*(1-y)/k_top above the interface, and
T(y)=300+q*(0.5/k_top+(0.5-y)/k_bottom) below it. The test checks every cell and
internal matrix face flux, not only the two boundary temperatures. Bottom inward
power must be +20 W and top inward power -20 W. Steady balances establish input
and output; they do not establish transient fluid/rock energy conservation.

Completed fresh build/run: `run-acceptance/` (22 serial, 4 MPI, 1 cyclic check).

- Uniform scalar/field max temperature error 5.18e-11 K.
- Layered max errors 3.88e-11 K (2/4) and 6.52e-11 K (4/2); all internal flux
  errors below 5e-10 W. Arithmetic-interpolation negative control has 0.04375 K
  maximum error, showing that the test detects interface-resistance errors.
- Physical patch conductivity 3..14 W/(m K), different from adjacent cells, works
  face by face for fixed/Gaussian/linear flux and field serialization/reload.
- Same-timestep doubling of reference values doubles kr_eff and halves the imposed
  gradient without changing specified heat input. This is a probe mutation, not
  a production conductivity law or time multiplier.
- Nonzero restart ignores corrupt saved kr_eff and reconstructs a deliberately
  corrupted temperature value/gradient before EOS evaluation. p/T/kr/kr_eff match
  uninterrupted stationary results exactly at saved precision; rho differs by
  at most 2.01e-10 kg/m3. Missing restart reference fails.
- Invalid source, absent reference/selected field, wrong dimensions, negative/
  zero/nonfinite conductivity fail. Excessive startup heat input fails at the
  physical EOS boundary at time 0, before pressure initialization.
- Legacy dictionary mode is retained even with registered conductivity fields.
- Full 9125-step h1: profile and p/T/U/rho/mu/phi byte-identical to the preserved
  baseline at saved precision. No legacy case scheme was edited.
- MPI checks cover a material discontinuity on the processor interface, serial/
  parallel field agreement, rank-local fatal termination, nonuniform flux
  decomposition and legacy-mode rank-local boundary diagnostics. The cyclic probe verifies standard coupled interpolation.

Earlier development evidence remains in `run-20261030/` and `run-20261029-final/`: a probe used the wrong
argList API initially; library-path precedence selected the installed old BC until
fixed; test solver dictionaries needed pFinal and a temperature solver supporting
asymmetric matrices; an unused copied h field had incompatible patch names; the
probe needed the deltaCoeffs overload of coupled snGrad; manual decomposition
required a quoted filename. Final error diagnostics use raw local face geometry. These were harness issues,
retained in logs. Production solver/library builds passed from the first build.

Scientific limits: restart/parallel HTFoam checks here are stationary; arbitrary
transient restart convergence, full energy budgets, nonlinear conductivity,
dynamic mesh mapping, coupled contact conditions and anisotropy are not established.
The existing initialization/coupling concerns and EOS limitations remain unchanged.

The initial conductivity review found an unresolved plain HydrothermalHeatFlux
copy-constructor symbol in both the original and updated libraries. The separately
accepted boundary-cloning commit resolves it and the equivalent symbols in all
three pressure BCs. The complete library now passes strict Linux ARM64 linking and
ldd -r. [Cloning regressions](../boundaryClones/README.md) cover the supported API.
All 27 conductivity checks pass against that rebuilt full library in
run-all-copyfixes/, with preserved h1 byte comparisons. Original investigation logs
remain local; this follow-up supersedes the earlier clone-path limitation.
