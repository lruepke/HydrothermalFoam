# HTFoam Modernization

## Overview

HTFoam has been modernized for **OpenFOAM Foundation 10** and the current **xThermo** library. It remains a solver for single-phase Darcy flow and heat transport in porous media, with pressure- and temperature-dependent fluid properties.

The modernization addresses several numerical and implementation problems, particularly in simulations with heterogeneous permeability and parallel domain decomposition. It also introduces spatially variable thermal conductivity, improves boundary-condition compatibility, and makes thermodynamic property evaluations more robust.

This document summarizes **what changed in the code, why it matters, and what users need to configure differently**.

## 1. Parallel permeability: domain-decomposition indexing bug

Testing parallel simulations with heterogeneous permeability revealed an indexing error in the original OpenFOAM Foundation 10 `decomposePar` utility.

In `fvFieldDecomposerDecomposeFields.C`, the original implementation used:

```cpp
owner[-addressing[i] + 1]
```

The correct expression is:

```cpp
owner[-addressing[i] - 1]
```

OpenFOAM encodes certain face addresses as negative integers. The incorrect expression selects the wrong owner cell when initializing processor-boundary values for volume fields.

**Why this matters:** After decomposition, the permeability values inside each processor domain can be correct while the values stored on processor boundaries are wrong. This can lead to incorrect interpolated Darcy mobility and mass fluxes, particularly across sharp permeability contrasts. A serial calculation can therefore produce the expected result while an otherwise identical parallel calculation does not.

The indexing error is present in the [original OpenFOAM 10 source](https://cpp.openfoam.org/v10/fvFieldDecomposerDecomposeFields_8C_source.html). It is corrected in [OpenFOAM 11](https://cpp.openfoam.org/v11/fvFieldDecomposerDecomposeFields_8C_source.html) and the [updated OpenFOAM 10 GitHub master branch](https://github.com/OpenFOAM/OpenFOAM-10/blob/master/applications/utilities/parallelProcessing/decomposePar/fvFieldDecomposerDecomposeFields.C). Thus, whether the error occurs depends on the OpenFOAM 10 source version installed.

### Correction in HTFoam

Rather than modifying the external OpenFOAM installation, HTFoam explicitly synchronizes permeability immediately after reading the field in `createFields.H`:

```cpp
permeability.correctBoundaryConditions();
```

This updates coupled processor-boundary values from the actual neighbouring cells before permeability is used in the Darcy mobility calculation. It applies at startup and on restart.

The correction has been verified for the maintained layered-permeability cases using serial, two-rank and four-rank simulations. It addresses the identified processor-boundary problem but does not introduce time-dependent permeability.

## 2. Correct reconstruction of Darcy velocity

A second important correction concerns the cell-centered Darcy velocity `U`.

HTFoam calculates the conservative mass flow rate `phi` through cell faces as part of the pressure solution. Previously, the solver reconstructed cell velocity indirectly using pressure and gravity contributions together with face and cell mobilities.

At sharp permeability contrasts, these operations are not equivalent. **The face mass flux could be correct while the reconstructed cell velocity was wrong.**

This is important because velocity is not merely an output field. It also enters the temperature equation through pressure-work and Darcy drag-heating terms. Errors in velocity can therefore affect temperature, thermodynamic properties and subsequent pressure solutions.

### Correction in HTFoam

Both `pEqn.H` and `initpEqn.H` now reconstruct velocity directly from the final face mass flux:

```cpp
U = fvc::reconstruct(phi)/rho;
```

Here, `phi` is the face mass flow rate [kg/s], `rho` is fluid density [kg/m³] and `U` is bulk Darcy velocity [m/s].

This makes the reconstructed cell velocity consistent with the mass flux calculated by the pressure equation. In the constant-property analytical layered-permeability benchmark, it recovers the expected uniform Darcy velocity across a permeability jump.

The correction also produced small, reproducible changes in some historical benchmark metrics. These were verified against the previous implementation; the independent HYDROTHERM reference data were not changed.

## 3. Darcy mobility at permeability interfaces

Correct processor-boundary values and velocity reconstruction are complemented by appropriate interpolation of the Darcy mobility.

The coefficient governing Darcy mass flux is

\[
M=\frac{\rho K}{\mu},
\]

where \(K\) is permeability [m²], \(\rho\) is fluid density [kg/m³] and \(\mu\) is dynamic viscosity [Pa·s].

Across a strong permeability contrast, arithmetic interpolation can give an incorrect effective resistance. The maintained layered benchmark therefore specifies harmonic interpolation in `system/fvSchemes`:

```foam
interpolate((rho*(permeability|mu))) harmonic;
```

The resulting face mobility is used consistently in the pressure Laplacian and the pressure and gravity flux calculations.

This is a **case-level numerical choice**, not a new global default.

For heterogeneous parallel calculations, three distinct requirements therefore matter:

1. Correct permeability values on processor boundaries.
2. Appropriate interpolation of Darcy mobility to cell faces.
3. Reconstruction of cell velocity from the final face mass flux.

## 4. Updated xThermo integration

HTFoam uses the current xThermo interface for fluid density, viscosity, heat capacity, thermal expansivity and compressibility.

The maintained setup supports the IAPS84 and IAPWS95 water-property backends. Pure water and fixed-composition H2O–NaCl fluids can be configured in `constant/xThermoProperties`.

For example, pure water with IAPS84:

```foam
fluid H2O;
backend IAPS84;
```

### Property updates and return-value checking

Thermodynamic properties are evaluated from the current pressure, temperature and composition during initialization and after pressure–temperature coupling passes.

The actual **xThermo library call**, in [evaluateFluidState.H](evaluateFluidState.H), is:

```cpp
status = thermo.tryUpdateState_TPX(state, T, p, X, &message);
```

Here `thermo` is the xThermo object passed as `*pxThermo` to HTFoam's checked wrapper, `HTFoamThermo::evaluate(...)`. [updateProps.H](updateProps.H) invokes that wrapper for each cell and physical boundary face at startup, at the end of each outer pressure-initialization iteration, and after each transient pressure → temperature pass. Coupled patches exchange the updated properties rather than performing separate face EOS evaluations. The wrapper checks the returned `EvaluationStatus`, phase and properties before the solver accepts `state`.

The important change is that every EOS evaluation now checks the returned status and validates the resulting state and properties. HTFoam checks for unsupported phases, invalid pressure or temperature, nonfinite values and physically invalid coefficients.

Invalid evaluations terminate the simulation with diagnostic information, rather than allowing erroneous properties to propagate silently into the solution.

The initial thermodynamic state is also evaluated from the actual case pressure and temperature, including relevant physical boundaries, before constructing the initial Darcy flux.

These changes improve robustness and error diagnosis; they do not alter the single-phase, fixed-composition nature of the solver.

## 5. Spatially variable thermal conductivity: `kr` and `kr_eff`

HTFoam now supports spatially varying thermal conductivity, for example in layered geological models.

The distinction between the fields is:

- **`kr`** is the prescribed bulk effective thermal conductivity [W/(m·K)].
- **`kr_eff`** is the derived field used in the temperature equation and available to heat-flux boundary conditions.

In the current implementation,

\[
k_{\mathrm{eff}}(\mathbf{x})=k_r(\mathbf{x}).
\]

No additional porosity-based conductivity mixing rule or temperature-dependent law is applied. Despite its historical name, `kr` already represents bulk effective conductivity, not the conductivity of individual rock grains.

### Uniform conductivity

Existing homogeneous cases can continue using the scalar `kr` in `constant/transportProperties`. The default behavior is equivalent to:

```foam
krSource uniform;
```

### Heterogeneous conductivity

Select field mode in `constant/transportProperties`, retaining the case's porosity and rock-storage entries:

```foam
krSource field;
```

Provide `kr` at the selected starting time. The following complete `0/kr` example uses a unit box, x/y/z = 0..1 m, with one cell through z and the patch names shown. Choose a mesh with a face at y=0.5 m; adapt patch names and coordinates for another geometry.

```foam
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      kr;
}

dimensions      [1 1 -3 -1 0 0 0];
internalField   uniform 2;

boundaryField
{
    left          { type zeroGradient; }
    right         { type zeroGradient; }
    bottom        { type zeroGradient; }
    top           { type zeroGradient; }
    frontAndBack  { type empty; }
}
```

Initialize two regions with this `system/setFieldsDict`: the lower half has 2 W/(m·K), and the upper half has 3 W/(m·K).

```foam
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      setFieldsDict;
}

defaultFieldValues
(
    volScalarFieldValue kr 2
);

regions
(
    boxToCell
    {
        box (0 0.5 0) (1 1 1);
        fieldValues
        (
            volScalarFieldValue kr 3
        );
    }
);
```

After mesh generation, run `setFields` before HTFoam. Merge these entries with any existing permeability initialization rather than replacing it. This example supplies only the conductivity inputs; the other case fields and dictionaries are still required. For parallel cases, use the mesh's corresponding coupled patch types.

The `zeroGradient` patches extend the adjacent material conductivity to the physical boundary. HTFoam corrects these and the coupled patch values, then copies the reference field into **`kr_eff = kr`**, without a porosity multiplier. Field-mode `kr` is written with saved times. A restart requires the `kr` field at the selected time, for example `1000/kr`; a saved `kr_eff` alone is insufficient because it is always rebuilt.

For layered conduction, harmonic interpolation can be selected in `system/fvSchemes`:

```foam
laplacian(kr,T) Gauss harmonic corrected;
```

Although the equation uses `kr_eff`, the scheme key remains `laplacian(kr,T)` for compatibility with existing case configurations.

## 6. Boundary-condition changes

The existing `hydrothermalHeatFlux` boundary condition can now use the local effective thermal conductivity:

```foam
conductivityField kr_eff;
```

This allows an imposed heat flux to be converted into a temperature gradient using the conductivity at each boundary face, rather than a single conductivity constant for the whole patch.

The legacy constant-conductivity mode remains available for compatibility, but HTFoam cases should explicitly select `kr_eff`.

The boundary-condition library was also adapted to OpenFOAM 10's copying and cloning interfaces. The affected conditions include `hydrothermalHeatFlux`, `noFlux`, `HydrothermalMassFluxPressure` and `submarinePressure`.

These are compatibility corrections rather than new physical boundary formulations. The heat-flux boundary condition also includes improved input validation and corrections to the handling and serialization of flux-profile parameters.

**Known limitation:** `submarinePressure` still has an issue when saving a nondefault `rhoValue` parameter for restart. Users relying on that parameter should check their saved boundary dictionaries.

## 7. Pressure initialization and pressure–temperature coupling

The initialization and transient coupling procedures have been made more explicit.

Optional pressure initialization can establish hydrostatic or pressure-driven initial conditions using the supplied initial temperature. It now has dedicated controls in `system/fvSolution`:

- `INIT.enabled`
- `INIT.maxIterations`
- `INIT.nCorrectors`
- `INIT.maxDeltaP`

This replaces reliance on the old PIMPLE outer-iteration state during initialization.

For transient calculations, the solver uses configurable Picard coupling:

**Pressure solve → temperature solve → xThermo property update.**

The number of passes per timestep is controlled by `PTCOUPLING.tightCouplingIters`. For example:

```foam
PTCOUPLING
{
    tightCouplingIters 4;
}
```

The value shown is illustrative. The appropriate iteration count and timestep must be assessed for the simulation. Pressure nonorthogonal corrections remain controlled separately through the relevant PIMPLE setting.

## 8. What users need to check

The maintained solver executable is **`HTFoam-review`**, built against OpenFOAM Foundation 10 and the matching xThermo and `libHydrothermalBoundaryConditions` installations.

When updating an existing case, review the following:

| Component | Required check |
|---|---|
| Thermodynamics | Configure the fluid, EOS backend and fixed composition in `xThermoProperties` |
| Conductivity | Use scalar `kr`, or set `krSource field;` and provide a spatial `kr` field |
| Heat-flux boundaries | Select `conductivityField kr_eff;` |
| Layered permeability | Review harmonic face-mobility interpolation in `fvSchemes` |
| Initialization | Review the `INIT` controls |
| Transient coupling | Review `PTCOUPLING.tightCouplingIters` |
| Parallel simulations | Use the updated permeability synchronization and verify the OpenFOAM decomposition version |
| Velocity output | Expect corrected cell-centered `U` values, particularly near permeability jumps |

Five tutorials are maintained: `Regular2DBox`, `Regular2DBox_layered`, `Regular2DBox_exp_perm`, `gmsh2DBox` and `3Dbox`. The 3D tutorial now uses pure water (`X=0`).

The `triToFoam` utility has been ported to OpenFOAM 10, providing a Triangle-based meshing route alongside Gmsh. Older cookbook cases are preserved separately but are not part of the maintained examples.

Build and installation instructions are available in the [root README](../../readme.md). Detailed case settings are described in [CaseConfiguration.md](CaseConfiguration.md).

## 9. Verification and remaining limitations

The modernized solver was compared against independent HYDROTHERM results for six 1D benchmarks (h1–h3 and v1–v3) and a homogeneous 2D convection simulation through 50 kyr.

Additional verification covers heterogeneous thermal conductivity, analytical Darcy flow across a 10:1 permeability contrast, and serial/MPI agreement.

The weekly scientific regression suite evaluates 60 numerical metrics and generates nine comparison images. All regression gates passed in the validated ARM64 container. Execution on an actual GitLab runner remains to be qualified.

The verification supports the specific corrections described here but does not establish mesh-independent accuracy or exact mass and energy conservation for every problem. Timestep sensitivity, nonlinear convergence, EOS mass-inventory discrepancies and some energy-discretization questions remain case dependent.

Further technical details and benchmark provenance are documented in [HTFoam_Background.md](HTFoam_Background.md) and the maintained benchmark reports.

**The most consequential changes are the correction of permeability processor-boundary values, appropriate face mobility across material interfaces, and reconstruction of cell velocity from the final conservative mass flux.** The other changes improve thermodynamic robustness, conductivity modeling, boundary-condition compatibility and solver configuration.