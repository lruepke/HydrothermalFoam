# HTFoam maintained-case manifest

Stage 2 support scope, updated 2026-11-02; current reviewed solver baseline `54eeea16`.
This manifest identifies configurations, not every directory under tutorials or
benchmarks. "Regression" means reproducible existing evidence, not a certified
continuum solution. The five cookbooks below have fresh-copy smoke qualification
(three hours for 2D, one hour for 3D);
this does not qualify their full-duration numerical accuracy. Their READMEs record
input compatibility changes and the exact preparation commands.
Configuration contract: [CaseConfiguration.md](CaseConfiguration.md).

Paths below are relative to the repository root. Generate fresh run directories;
never run cleaning scripts in original cases or replace preserved baselines.

| ID / status | Source configuration | Supported purpose / limits |
|---|---|---|
| H1 / compatibility regression | `benchmarks/HTFoam/HydrothermalFoam/1d/h1` | Original compatibility settings, 250 legacy 365-day years; retain the initialization warning. |
| H2 / practical regression | `benchmarks/HTFoam/HydrothermalFoam/1d/h2` | Accepted 198-cell aligned-boundary, four-pass, 5-day case; 120 Julian years. |
| H3 / transport regression | `benchmarks/HTFoam/HydrothermalFoam/1d/h3` | Accepted 1500-year configuration, three passes and steady pressure initialization. |
| V1 / gravity regression | `benchmarks/HTFoam/HydrothermalFoam/1d/v1` | Matched-input 750-year case; INIT disabled and four passes. |
| V2 / reporting regression | `benchmarks/HTFoam/HydrothermalFoam/1d/v2` | Matched-input 350-year case including the final 7.5-day step; sharp-front accuracy remains manual qualification. |
| V3 / reporting regression | `benchmarks/HTFoam/HydrothermalFoam/1d/v3` | Matched-input 1500-year case; EOS storage error decreases with timestep refinement but is not demonstrated converged and is not an acceptable conservation tolerance. |
| 2D / convection regression | `benchmarks/HTFoam/HydrothermalFoam/2d` | Accepted original-top y=0 case; 5/15/50 kyr stages. The aligned sensitivity case is archived, not substituted. |
| 3D / retained definitions | `benchmarks/HTFoam/HydrothermalFoam/3d` | Historical inputs retained unchanged; current solver/mesh qualification remains outstanding. |
| Hydrostatic / verification | `solvers/HTFoam/tests/initialization/run_tests.py` | Existing 1 m column, gravity, 300 K, top 30 MPa, no-flow base; initialization/restart/multiple-corrector checks. Not an independent EOS test. |
| Layered conductivity / verification | `solvers/HTFoam/tests/conductivity/run_tests.py` | Existing 2/4 W/(m K) layers, unequal spacing, harmonic faces, restart, cyclic and two-rank interface checks. This conductivity-specific MPI check is effectively 1D; separate 2D permeability/MPI evidence is listed below. |
| Box-uniform / smoke-qualified tutorial | `tutorials/cookbooks/2d/Regular2DBox` | Uniform-permeability 2D example; original thermal boundaries/materials preserved; explicit skipped initialization and three Picard passes. |
| Box-layered / smoke-qualified tutorial | `tutorials/cookbooks/2d/Regular2DBox_layered` | 100x50, 2x1 km; permeability 1e-14 below y=-3000 and 1e-13 above. This is permeability layering, not heterogeneous conductivity. |
| Box-exponential / smoke-qualified tutorial | `tutorials/cookbooks/2d/Regular2DBox_exp_perm` | Runtime depth-dependent permeability; unchanged 1000 C basal temperature passes the short EOS check, not full-duration qualification. |
| Gmsh/Triangle / smoke-qualified tutorial | `tutorials/cookbooks/2d/gmsh2DBox` | One physical case and solver configuration; independently regenerated Gmsh or Triangle meshes. Original pure water now uses xThermo H2O/IAPS84. |
| 3Dbox / smoke-qualified tutorial | `tutorials/cookbooks/3Dbox` | Original geometry, heating and material values; approved salinity X=0 replaces .2 because the original hot state is vapor + halite. Serial and short two-rank workflow; no full-duration qualification. |
| Layered permeability / verification | `benchmarks/HTFoam/HydrothermalFoam/2d-layered` | Analytical harmonic transmissibility, discrete interface flux and short serial/2-/4-rank startup/restart checks pass. No hot-plume crossing, spatial convergence or EOS mass-conservation acceptance claim. |

## Benchmark use and qualification

One maintained case directory per benchmark; direct run/plot commands and reference
identities are in the [short suite README](../../benchmarks/HTFoam/README.md).
Default p/T comparisons reproduce the accepted primary metrics; they do not
establish conservation. h1-h3 remain horizontal transport cases and v1-v3 forced
vertical gravity/transport cases. All six full 1D runs are affordable weekly for
repeatability, completion and EOS guards. Reference/grid/time convergence,
v2 front shape and v3 storage convergence remain extended/manual qualification.
The retained 3D definitions are outside the current validated execution set.

## Applied cookbook compatibility updates

Use each of the five cookbook READMEs for fresh-copy prepare/run/ParaView commands.
The scripts use HTFoam-review and a matching shared boundary library, refuse the
tracked source case or an existing mesh, and never invoke the old clean scripts.
Gmsh and Triangle are independent mesh options in the same imported-mesh case.

The three regular 2D boxes and 3Dbox retain disabled initialization and three
Picard passes. Gmsh retains one initialization outer pass/two pressure correctors
and one transient pass; its initialization warning is expected, not convergence.
Original time controls, relaxation and schemes remain, except the layered and
exponential cases' explicit harmonic Darcy mobility. Smoke mode uses three fixed one-hour steps in
the 2D run copy (one step for 3D); it does not qualify the original long-duration timestep caps.

Original material values, physical boundaries and geometry are preserved. The
Gmsh case's new transport dictionary copies its legacy porousMedia entries; its
pure-water EOS compatibility choice is now explicit H2O/IAPS84. The other boxes
retain H2O-NaCl/IAPS84 at X=0 and uniform kr=1.5 W/(m K).
submarinePressure still gives 24.943825 MPa at y=-2500 m, regardless of the saved
30 MPa placeholder; its rhoValue restart serialization limitation remains.
3Dbox retains geometry and heating with the separately approved X=.2 to X=0
change, documented in its README. None uses the heat-flux BC; no thermal
boundary is replaced. The [maintained tutorial list](../../readme.md#five-maintained-tutorials) lists exactly
five supported examples. Other cookbooks are preserved byte-for-byte under
`tutorials/old/cookbooks/` and are historical/unqualified.

## Deferred or excluded from this first support set

- Original legacy vertical inputs are preserved in Git and the verified archive;
  support targets the canonical
  matched-input v1-v3 cases above. They are forced gravity/transport cases,
  not hydrostatic equilibrium. Enthalpy solvers and tutorials/old remain excluded.
- Regular2DBox_exp_perm: runtime compilation and the 1000 C basal model-edge
  state pass the short smoke; full-duration hot-flow qualification remains separate.
- Archived 3Dbox_par and the remaining old cookbooks are unqualified; their
  numerical/physical settings were not substituted into maintained examples.
- Short 2D layered MPI verification is complete. Further heated hydrostatic tests
  and a 3D extension remain separate qualification work.
- Broader cookbook directories have no implied maintenance status. CI scheduling,
  environment/image pinning and cross-platform acceptance tolerances remain separate work.

See the [suite README](../../benchmarks/HTFoam/README.md) for the simple maintained
workflow and scientific limits. Earlier workflows, sensitivity experiments and
legacy formulations remain in Git and the verified local source archive.
CI scheduling and acceptance tolerances remain separate reviewed work.
