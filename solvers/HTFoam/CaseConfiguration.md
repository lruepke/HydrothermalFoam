# HTFoam case configuration

Stage 2 guide, checked against solver source at `3326fd25` (2026-10-31).
For single-phase porous-media thermal convection, OpenFOAM **Foundation 10** and
the reviewed xThermo installation. Use `HTFoam-review` and its matching isolated
boundary library; preserve installed solvers and existing benchmark runs.
Supported configurations and pending tutorial work: [MaintainedCases.md](MaintainedCases.md).

## Required inputs and units

At the selected start time provide `p` (absolute Pa), `T` (K), and scalar
`permeability` (m2). Provide `constant/g`, `transportProperties` and
`xThermoProperties`. `U` is Darcy velocity (m/s), not pore velocity; it is optional
and defaults to zero. `phi` is integrated face **mass flow** (kg/s), read if
present or initially constructed from rho/U. EOS properties are recomputed from
p/T, not read from saved rho/mu. There is no salt transport or tensor permeability.

## Initialization, coupling and linear controls

These are custom loops, not a running `pimpleControl` algorithm. `PIMPLE` must
exist. INIT/PTCOUPLING entries below are read at startup; changing them during a
run does not update the transient loop counts.

| Entry | Implemented behavior |
|---|---|
| `INIT.enabled` | Default true. Initialization is entered only at time name `"0"`; nonzero restart skips it. |
| `INIT.maxIterations` | Outer initialization budget; overrides `PIMPLE.nOuterCorrectors`, default 1. Zero skips. |
| `INIT.nCorrectors` | Overrides `PIMPLE.nCorrectors`, default 1; zero still gives one inner pressure corrector. |
| `INIT.maxDeltaP` | Absolute Pa; overrides `PTCOUPLING.maxDeltaP`. Stops when max internal pressure change is strictly smaller. |
| Missing pressure-change target | Completes the budget and warns that convergence was not assessed. |
| Initialization exhaustion | Warns and continues. Density/mobility changes and max divergence of solved phi are diagnostics only. |
| `PIMPLE.nNonOrthogonalCorrectors N` | N+1 pressure solves per inner initialization corrector and per transient Picard pass. Use nonnegative N. |
| `PTCOUPLING.tightCouplingIters K` | Total p -> T -> EOS passes per step. Missing, zero or negative K gives one pass. No nonlinear early exit or residual stopping. |
| `PTCOUPLING.maxInitOuterIters` | Unused, with a migration warning. Use `INIT.maxIterations`. |
| PIMPLE residual controls | Neither `residualControl` nor `outerCorrectorResidualControl` controls these loops. |
| Linear solvers | Ordinary `solvers.p` and `solvers.T` entries are used; pFinal/TFinal are not selected by the custom loops. |
| Matrix relaxation | `relaxationFactors.equations` for p/T is honored. Factor 1 disables effective relaxation. |

Initialization freezes EOS-derived mobility/density/gravity coefficients across
inner pressure and nonorthogonal corrections, then evaluates EOS once at the end
of each outer iteration. The next outer iteration uses those updated properties.
Transient passes solve pressure, then temperature, then update EOS. Final rho/mu
therefore need not exactly match the coefficient snapshot that produced phi/U;
inspect Picard changes rather than assuming convergence from the pass count.

Example `system/fvSolution` for a small orthogonal verification case, not a
retroactive change to accepted baselines. The initialization target is an example,
not a mandatory universal tolerance. Initialization/nonorthogonal counts must
be nonnegative; initialization also rejects nonfinite/negative pressure targets.

```foam
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    p { solver GAMG; smoother DICGaussSeidel; tolerance 1e-10; relTol 0; }
    T { solver PBiCGStab; preconditioner DILU; tolerance 1e-10; relTol 0; }
}
PIMPLE { nNonOrthogonalCorrectors 0; }
INIT { enabled true; maxIterations 40; nCorrectors 1; maxDeltaP 0.01; }
PTCOUPLING { tightCouplingIters 4; }
relaxationFactors { equations { p 1; T 1; } }
```

A steady all-Neumann initialization needs a pressure anchor/appropriate constraint;
HTFoam does not automatically install a pressure reference. Do not interpret a
small linear residual alone as converged hydrostatics or EOS consistency.

## Time stepping, Courant number and schemes

`controlDict` uses seconds. `adjustTimeStep` defaults false, `maxCo` defaults 1,
and `maxDeltaT` defaults to a very large limit. These three entries are reread
each time step, subject to normal OpenFOAM dictionary rereading. If adjustment
is disabled, maxCo/maxDeltaT do not provide adaptive protection.

With adjustment enabled, Foundation 10 uses the available previous flux/rho to
limit dt, applies fvModels limits and maxDeltaT, and damps increases to at most
20% per step. Write-time alignment can also change dt. At zero initial flow,
the first actual step can grow from the configured starting deltaT.

The active maximum is `max_i[dt * sum_faces(abs(phi)) / (2*rho_i*V_i)]`.
There is **no porosity divisor**, so this is a bulk Darcy-flow measure, not a
pore-velocity or thermal-storage Courant number. Weak flow does not establish
conduction accuracy; retain a tested dt cap and perform time-step sensitivity.
`porousCourantNo.H` is not included; its current mass-flux expression must not be
enabled as if it were a verified alternative.

The reviewed 2D benchmark uses initial deltaT=3155760 s, adjustment enabled,
maxCo=.2 and maxDeltaT=315576000 s. h2's practical baseline instead uses fixed
deltaT=432000 s and exact endTime=3786912000 s. One reference year is 31557600 s.

Example `system/fvSchemes` uses the verified **Euler** scope and explicit keys:

```foam
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; }
divSchemes
{
    default none;
    div((phi*interpolate(Cp)),T) Gauss upwind;
}
laplacianSchemes
{
    default none;
    laplacian(rhorAUf,p) Gauss linear corrected;
    laplacian(kr,T) Gauss harmonic corrected;
}
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
fluxRequired { default no; p; }
```

The actual time keys are `ddt(p)` and `ddt(T)`; storage coefficients multiply
those operators externally. Other ddt schemes are not certified by these tests.
Pressure mobility is already a face field, constructed by interpolating
rho*(permeability/mu); its interpolation follows the interpolation scheme lookup.
The harmonic temperature entry does not change pressure mobility interpolation.
Keep accepted cases' existing upwind/vanLeer, correction and interpolation choices
unless a separately reviewed numerical experiment calls for changes.

## Conductivity examples

Uniform `constant/transportProperties` (the omitted krSource defaults to uniform):

```foam
FoamFile { version 2.0; format ascii; class dictionary; object transportProperties; }
porosity porosity [0 0 0 0 0 0 0] 0.1;
rho_rock rho_rock [1 -3 0 0 0 0 0] 2700;
cp_rock cp_rock [0 2 -2 -1 0 0 0] 880;
krSource uniform;
kr kr [1 1 -3 -1 0 0 0] 2;
```

For heterogeneous conductivity, keep the same material entries but replace
`krSource uniform;` with `krSource field;`. The scalar kr entry may be removed;
if retained it is ignored in field mode. Supply the following `0/kr` for a
compatible unit-height 2D box with patches left/right/top/bottom/frontAndBack:

```foam
FoamFile { version 2.0; format ascii; class volScalarField; object kr; }
dimensions [1 1 -3 -1 0 0 0];
internalField uniform 2;
boundaryField
{
    left { type zeroGradient; }
    right { type zeroGradient; }
    top { type zeroGradient; }
    bottom { type zeroGradient; }
    frontAndBack { type empty; }
}
```

Example `system/setFieldsDict` puts 2 W/(m K) below y=.5 and 4 above it. Use a
mesh aligned with the interface, then run `setFields` after `blockMesh` and before
the solver. If a case already initializes permeability this way, combine both
fields in its setFields dictionary rather than replacing its permeability setup.

```foam
FoamFile { version 2.0; format ascii; class dictionary; object setFieldsDict; }
defaultFieldValues (volScalarFieldValue kr 2);
regions
(
    boxToCell
    {
        box (0 0.5 0) (1 1 1);
        fieldValues (volScalarFieldValue kr 4);
    }
);
```

Use `laplacian(kr,T) Gauss harmonic corrected;` as above. The solver explicitly
selects **laplacian(kr,T)** even though the coefficient is named **kr_eff**;
an entry only for laplacian(kr_eff,T) will not select this operator. Foundation
10's harmonic scheme interpolates reciprocal conductivity with reverseLinear
and takes its reciprocal. On an orthogonal interface, this gives
`k_face=(d_owner+d_neighbour)/(d_owner/k_owner+d_neighbour/k_neighbour)`:
series thermal resistance, including unequal cell-centre distances. Arithmetic
averaging generally gives the wrong interface conductance. Uniform k gives the
same harmonic/linear face value; this is not authorization to edit legacy schemes.

The following complete `0/T` matches those unit-box patch names, fixes the top
at 300 K and imposes basal inward q=20 W/m2 through the registered coefficient:

```foam
FoamFile { version 2.0; format ascii; class volScalarField; object T; }
dimensions [0 0 0 1 0 0 0];
internalField uniform 300;
boundaryField
{
    left { type zeroGradient; }
    right { type zeroGradient; }
    top { type fixedValue; value uniform 300; }
    bottom
    {
        type hydrothermalHeatFlux;
        conductivityField kr_eff;
        shape fixed;
        q uniform 20;
        value uniform 300;
    }
    frontAndBack { type empty; }
}
```

These are configuration examples for an existing compatible case, not a complete
solver case: mesh, p, permeability, g and controlDict are still required. For
stationary pure conduction the layer order above gives interface T=302.5 K and
base T=307.5 K; uniform k=2 gives base T=310 K. These references assume no
advective/transient/dissipative contribution, not an arbitrary hydrothermal run.

Both conductivity modes mean finite positive **bulk** W/(m K), with no new law
or porosity multiplier. The updater creates kr_eff before T, refreshes it before
T boundary evaluation/assembly, copies physical kr patch values and communicates
coupled patches. ZeroGradient extends the adjacent material; use explicit patch
values only for an intended different boundary conductivity. Reference kr BCs
must not depend on T or kr_eff: that would violate startup ordering. Use matching
processor/cyclic/empty constraints when decomposing or changing mesh topology.

On restart, field mode requires saved kr at the selected time; uniform mode
ignores saved kr fields. kr_eff is always rebuilt. There is no automatic loading
of a new internal kr field from later time folders, runtime uniform-scalar refresh,
temperature dependence or time multiplier. Dynamic boundary laws are reevaluated,
but are not a substitute for an implemented internal constitutive update.

## xThermo and physical boundaries

Pure-water `constant/xThermoProperties`:

```foam
FoamFile { version 2.0; format ascii; class dictionary; object xThermoProperties; }
fluid H2O;
backend IAPS84;
```

Pure water also accepts IAPWS95 (water/Water are H2O aliases); CoolProp is not a
supported pure-water selection in this solver. A brine example is:

```foam
FoamFile { version 2.0; format ascii; class dictionary; object xThermoProperties; }
fluid H2O-NaCl;
backend IAPS84;
H2O-NaCl { constX 0.1; }
```

constX is fixed kg/kg in [0,1]; missing brine composition defaults to zero with a
warning. Brine backend construction is delegated to xThermo; use the audited
IAPS84/IAPWS95 configurations, not backend names inferred from old comments.
Pin the installed library revision and rebuild when switching static libraries.
Finite positive p/T are necessary but insufficient: advertised model bounds,
status/exceptions, supported fluid phase and finite rho/mu/Cp/betaT/alphaP are
checked. rho/mu/Cp/betaT must be positive; alphaP may be negative or zero. Exact
Critical, multiphase, solid and unknown states are rejected. No clipping or retry.
See xThermo's MODEL_SPECIFICATION/OUTSTANDING_DEFECTS: low-pressure brine negative
compressibility and cold-IAPWS95-brine/domain-edge restrictions remain relevant.
Passing guards does not establish EOS accuracy.

Physical property faces are evaluated from boundary p/T; coupled properties are
communicated, not reevaluated from averaged p/T. Empty patches are skipped.
Temperature inletOutlet patches depend on phi; startup selectively evaluates the
heat-flux patches first rather than prematurely evaluating all T patches.

| Boundary | Requirement / meaning |
|---|---|
| Fixed p/T | Absolute Pa and K. Choose a pressure datum/anchor deliberately. |
| Pressure `noFlux` | Uses named face fields phig/rhorAUf to cancel gravity mass flux; zeroGradient p is generally not impermeable under gravity. |
| `hydrothermalMassFluxPressure` | q is signed outward **kg/s per face**, as subtracted from phig; not flux density. Uses phig/rhorAUf. |
| T `inletOutlet` | Prescribed inlet T, zero-gradient outflow; not equivalent to fixed T on both inflow and outflow. |
| `hydrothermalHeatFlux` | q is inward W/m2; outward-normal T gradient=q/kr_eff, evaluated face by face. Fixed shape accepts a facewise q list. Other supported shapes: gaussian2d, gaussian3d, linear2d. |
| Heat-flux legacy mode | Without conductivityField, requires registered thermophysicalProperties/mixture/porousMedia/<kr>. HTFoam does not register that dictionary; a file alone is insufficient. Select kr_eff explicitly. |
| `submarinePressure` | Replaces value with 100000 + rhoValue*(g dot faceCentre) Pa; rhoValue defaults 1013 kg/m3. Origin-dependent, not an EOS seawater column. |

Known submarinePressure restart defect: constructor reads `rhoValue`, but write()
emits `rhoValue_`. A nondefault rhoValue can revert to 1013 on restart. The
atmospheric constant is fixed in code. No BC fix is part of this documentation
increment; use fixed absolute p for verification requiring an unambiguous datum,
or explicitly account for this limitation without silently changing tutorial physics.

## Source and verification scope

Contracts above come from [HTFoam.C](HTFoam.C), [initpEqn.H](initpEqn.H),
[pEqn.H](pEqn.H), [TEqn.H](TEqn.H), [createFields.H](createFields.H),
[createConductivity.H](createConductivity.H), [updateConductivity.H](updateConductivity.H),
[createxThermo.H](createxThermo.H), [evaluateFluidState.H](evaluateFluidState.H),
[updateProps.H](updateProps.H), and the shared [boundary library](../../libraries/BoundaryConditions).
Courant/adaptive/ddt/harmonic behavior was checked against Foundation 10 sources.
Existing analytical, startup, MPI and regression evidence is under [tests](tests)
and the [benchmark validation index](../../benchmarks/HTFoam/README.md).
No new scheme, convergence tolerance, conductivity law or tutorial migration is
established by the examples. Initialization exhaustion and finite Picard changes
must remain visible; Euler testing does not validate other temporal schemes.
