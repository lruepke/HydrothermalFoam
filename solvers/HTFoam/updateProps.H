{
    // Preserve the existing field-copy/assignment sequence and patch types.
    volScalarField rhoUpdated = rho;
    volScalarField muUpdated = mu;
    volScalarField betaTUpdated = betaT;
    volScalarField alphaPUpdated = alphaP;
    volScalarField CpUpdated = Cp;

    forAll(rhoUpdated, cellI)
    {
        const HTFoamThermo::Location location =
            {mesh, cellI, -1, -1, "internal property update"};
        const auto state = HTFoamThermo::evaluate
        (
            *pxThermo, xThermoFluidName, xThermoBackend,
            T[cellI], p[cellI], constX, location
        );
        rhoUpdated[cellI] = state.Rho;
        muUpdated[cellI] = state.Mu;
        betaTUpdated[cellI] = state.IsothermalCompressibility;
        alphaPUpdated[cellI] = state.IsobaricExpansivity;
        CpUpdated[cellI] = state.Cp;
    }

    forAll(rhoUpdated.boundaryField(), patchI)
    {
        const fvPatch& patch = mesh.boundary()[patchI];
        // Coupled values come from property-field communication, after all
        // local internal values have been assigned. Empty patches have no data.
        if (patch.coupled() || isA<processorFvPatch>(patch)
         || isA<emptyFvPatch>(patch))
        {
            continue;
        }
        forAll(rhoUpdated.boundaryField()[patchI], faceI)
        {
            const HTFoamThermo::Location location =
                {mesh, -1, patchI, faceI, "physical boundary property update"};
            const auto state = HTFoamThermo::evaluate
            (
                *pxThermo, xThermoFluidName, xThermoBackend,
                T.boundaryField()[patchI][faceI],
                p.boundaryField()[patchI][faceI], constX, location
            );
            rhoUpdated.boundaryFieldRef()[patchI][faceI] = state.Rho;
            muUpdated.boundaryFieldRef()[patchI][faceI] = state.Mu;
            betaTUpdated.boundaryFieldRef()[patchI][faceI] = state.IsothermalCompressibility;
            alphaPUpdated.boundaryFieldRef()[patchI][faceI] = state.IsobaricExpansivity;
            CpUpdated.boundaryFieldRef()[patchI][faceI] = state.Cp;
        }
    }

    rho = rhoUpdated;
    mu = muUpdated;
    betaT = betaTUpdated;
    alphaP = alphaPUpdated;
    Cp = CpUpdated;

    // Keep this order identical on every rank. No reductions precede failures.
    rho.correctBoundaryConditions();
    mu.correctBoundaryConditions();
    betaT.correctBoundaryConditions();
    alphaP.correctBoundaryConditions();
    Cp.correctBoundaryConditions();

    forAll(rho.boundaryField(), patchI)
    {
        forAll(rho.boundaryField()[patchI], faceI)
        {
            xThermal::ThermodynamicProperties state;
            state.Rho = rho.boundaryField()[patchI][faceI];
            state.Mu = mu.boundaryField()[patchI][faceI];
            state.Cp = Cp.boundaryField()[patchI][faceI];
            state.IsothermalCompressibility = betaT.boundaryField()[patchI][faceI];
            state.IsobaricExpansivity = alphaP.boundaryField()[patchI][faceI];
            const HTFoamThermo::Location location =
                {mesh, -1, patchI, faceI, "corrected boundary properties (phase not communicated)"};
            HTFoamThermo::checkProperties
            (
                state, xThermoFluidName, xThermoBackend,
                T.boundaryField()[patchI][faceI],
                p.boundaryField()[patchI][faceI], constX, location
            );
        }
    }
}
