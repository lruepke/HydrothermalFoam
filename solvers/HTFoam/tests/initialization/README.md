# Explicit initialization verification

Use bash and source `/Volumes/OpenFoam/OpenFOAM-10/etc/bashrc`. Set `xThermo_DIR`
to the installed xThermo prefix. Build into a new ignored directory; installed
executables and preserved runs are never overwritten:

```bash
bash solvers/HTFoam/tests/conductivity/build.sh "$PWD/solvers/HTFoam/tests/conductivity/run-init-NAME"
python3 solvers/HTFoam/tests/initialization/run_tests.py \
  --build solvers/HTFoam/tests/conductivity/run-init-NAME \
  --run solvers/HTFoam/tests/initialization/run-NAME
python3 solvers/HTFoam/tests/conductivity/run_tests.py \
  --run solvers/HTFoam/tests/conductivity/run-init-NAME
```

The final command includes the full 9125-step h1 regression against compact tracked
fixtures. Optional `--old-solver /absolute/path/HTFoam-review` on the initialization
runner demonstrates the old early-exit and zero-outer-count `pFinal`/`TFinal`
selection; it is not required for default checks. Both executables use the same
isolated shared library. All generated inputs, output and logs are under `run-*`.

The runner enables Foundation 10's `solution` debug switch through a process-local
`FOAM_CONTROLDICT` (installation dictionary plus the switch). It checks actual
`Lookup solver for ...` messages, including after nonzero restart. No installation
configuration is edited. It verifies early exit, explicit budget exhaustion,
legacy zero count, explicit disablement and a gravity-driven hydrostatic column.
Hydrostatics checks the discrete pressure gradient against interpolated density
and the resulting Darcy velocity; it is not an independent EOS accuracy test.

## Controls

At time name `0` only, the solver initializes unless disabled:

```text
INIT
{
    enabled       true;
    maxIterations 40;
    nCorrectors   1;
    maxDeltaP     1e-6;  // Pa; example for the small hydrostatic test, not a general default
}
```

`INIT.maxIterations` overrides `PIMPLE.nOuterCorrectors` (default 1).
Zero means skip. `INIT.nCorrectors` overrides `PIMPLE.nCorrectors` (default 1);
zero retains the legacy minimum of one pressure solve. Negative counts are errors.
`PIMPLE.nNonOrthogonalCorrectors` retains its existing N+1 convention.
`INIT.maxDeltaP` overrides `PTCOUPLING.maxDeltaP`. When configured, it retains the
legacy strict pressure-change stopping test; density/mobility changes and mass
imbalance are diagnostic only. Without a target, the explicit budget is completed
and a warning reports that convergence was not assessed. Exhaustion warns and
continues: no new tight convergence criterion is mandatory.

`PTCOUPLING.maxInitOuterIters` remains unused, with a migration warning; it was not
functional previously. Set `INIT.maxIterations` explicitly to activate a different
budget. PIMPLE residual controls no longer instantiate native convergence logic;
they do not control initialization. Linear tolerances still come from `solvers.p`.

Nonzero restart skips initialization exactly as before, even if INIT is enabled.
No final-iteration flag is created. Ordinary transient `p` and `T` entries are used
consistently; cases that depended on the old leaked flag may need ordinary solver
tolerances adjusted. No automatic new use of `pFinal`/`TFinal` is introduced.

Pressure coefficients are constructed once per outer initialization iteration
and frozen through all inner pressure correctors and non-orthogonal passes.
Startup supplies the first EOS state; one EOS evaluation after the inner loops
supplies diagnostics and the next outer coefficient snapshot. There are no EOS
updates inside either inner loop. Equation, flux reconstruction,
relaxation calls and transient Picard coupling are unchanged. Initialization does
not add a pressure reference for closed all-Neumann systems. Final EOS properties
can still differ from the coefficient snapshot used for the last flux; inspect
reported property changes. `max|div(phi)|` diagnoses that solved flux, not a newly
reassembled final-EOS flux or a global conservation certificate.

Unlike the old implicit `GREAT` threshold, absence of `maxDeltaP` no longer claims
convergence after one pass. It completes the configured budget and warns. Native
`outerCorrectorResidualControl` termination is also no longer applied indirectly.

## Previous per-corrector-update results (superseded)

Isolated macOS/OpenFOAM Foundation 10 run (`run-acceptance`, build
`../conductivity/run-init-explicit-v2`): 11 focused checks pass, including three
optional old-executable comparisons. Ordinary p/T lookup is verified on every new
solver path; the old executable selects final entries on early exit and zero
outer count, and ordinary entries after normal exhaustion.

The 1 m hydrostatic column at 300 K and 30 MPa top pressure reaches a 1e-6 Pa
pressure-change target in 4 outer iterations. Maximum discrete gradient error
is 1.2233e-4 Pa/m and maximum velocity is 2.7917e-18 m/s. Restart pressure drift
is 1.0022e-6 Pa. Two pressure correctors reach the same target in 9 outer
iterations and differ from the one-corrector result by at most 1.0022e-6 Pa;
extra solves are not guaranteed to accelerate convergence near roundoff.

The existing 22-check serial conductivity suite, including full h1, passes.
All h1 compact-fixture errors are zero and final p/T/U/rho/mu/phi and sampled
profile are byte-identical to the preserved full old baseline. Its legacy single
initialization pass still changes pressure by 2.49629e7 Pa, density by 1.3258%
and mobility by 3.06605%; it now clearly warns that the 10 Pa target was not met
and continues. No stricter initialization acceptance is inferred from this
transport regression. No new parallel or Linux run was performed for this increment.

## Frozen-coefficient update results

Fresh build `../conductivity/run-init-frozen` and checks in `run-frozen` pass:
11 initialization checks and all 22 existing serial conductivity/h1 checks.
The multiple-corrector check additionally compares the first outer pressure
change with the one-corrector case: difference 9.02e-7 Pa, below 1e-4 Pa and well
below the roughly 0.02 Pa effect of updating density between those solves.

The one-corrector hydrostatic saved fields p/T/rho/mu/U/phi are numerically
identical to the previous explicit implementation. The two-corrector case reaches
the same pressure-change target in 3 outer iterations (previously 9); final
pressure differs by at most 1.003e-6 Pa, temperature is unchanged, and velocity
differs by at most 4.092e-18 m/s. Restart pressure drift remains 1.003e-6 Pa and
ordinary p/T dictionary selection is retained on all tested new-solver paths.
Full h1 final fields and sampled profile remain byte-identical to the preserved
old baseline. No convergence thresholds or other numerical settings changed.
