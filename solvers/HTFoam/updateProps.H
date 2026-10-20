{
    double h; // h: enthalpy
    double T0, p0;

    // Copy the rho field to update it
    // LHR: I did this to avoid sequential access to the rho field, which may cause problems in parallel runs (but that's just a guess)
    volScalarField rhoUpdated = rho;
    volScalarField muUpdated = mu;
    volScalarField betaTUpdated = betaT;
    volScalarField alphaPUpdated = alphaP;
    volScalarField CpUpdated = Cp;

    // 1. Update internal values
    forAll(rhoUpdated, i)
    {
        T0 = T[i];
        p0 = p[i];

        // Check valid pressure and temperature ranges (local check)
        if (p0 > pxThermo->pmax() || p0 < pxThermo->pmin() || T0 > pxThermo->Tmax() || T0 < pxThermo->Tmin())
        {
            FatalErrorInFunction
                << "Error in xThermo("
                << pxThermo->name()
                << "): Valid range for p is [" << pxThermo->pmin() << ", " << pxThermo->pmax()
                << "], T is [" << pxThermo->Tmin() << ", " << pxThermo->Tmax()
                << "]. Found p = " << p0 << ", T = " << T0
                << abort(FatalError);
        }

        // Update fluid properties
        props = pxThermo->UpdateState_TPX(T0, p0, constX);

        rhoUpdated[i] = props.Rho;
        muUpdated[i] = props.Mu;
        betaTUpdated[i] = props.IsothermalCompressibility;
        alphaPUpdated[i] = props.IsobaricExpansivity;
        CpUpdated[i] = props.Cp;
    }

    // 2. Update boundary values
    forAll(rhoUpdated.boundaryFieldRef(), patchI)
    {
        const fvPatch& patch = rhoUpdated.boundaryField()[patchI].patch(); // Access fvPatch

        if (!isA<processorPolyPatch>(patch)) // Skip processor patches, so that those are treated by the correctBoundaryConditions statements below
        {
            forAll(rhoUpdated.boundaryFieldRef()[patchI], faceI)
            {
                T0 = T.boundaryFieldRef()[patchI][faceI];
                p0 = p.boundaryFieldRef()[patchI][faceI];

                // Check valid pressure and temperature ranges (local check)
                if (p0 > pxThermo->pmax() || p0 < pxThermo->pmin() || T0 > pxThermo->Tmax() || T0 < pxThermo->Tmin())
            {
                    FatalErrorInFunction
                        << "Error in xThermo("
                        << pxThermo->name()
                        << "): Valid range for p is [" << pxThermo->pmin() << ", " << pxThermo->pmax()
                        << "], T is [" << pxThermo->Tmin() << ", " << pxThermo->Tmax()
                        << "]. Found p = " << p0 << ", T = " << T0
                        << " on patch " << patch.name() << ", face " << faceI
                        << abort(FatalError);
            }

                // Update fluid properties
            props = pxThermo->UpdateState_TPX(T0, p0, constX);

                //Info << "props.Rho = " << props.Rho << endl;

                rhoUpdated.boundaryFieldRef()[patchI][faceI] = props.Rho;
                muUpdated.boundaryFieldRef()[patchI][faceI] = props.Mu;
                betaTUpdated.boundaryFieldRef()[patchI][faceI] = props.IsothermalCompressibility;
                alphaPUpdated.boundaryFieldRef()[patchI][faceI] = props.IsobaricExpansivity;
                CpUpdated.boundaryFieldRef()[patchI][faceI] = props.Cp;
            }
        }
        }

    // 3. Assign updated fields back to the originals
    rho = rhoUpdated;
    mu = muUpdated;
    betaT = betaTUpdated;
    alphaP = alphaPUpdated;
    Cp = CpUpdated;

    // 4. Correct boundary conditions including processor patches
    rho.correctBoundaryConditions();
    mu.correctBoundaryConditions();
    betaT.correctBoundaryConditions();
    alphaP.correctBoundaryConditions();
    Cp.correctBoundaryConditions();


    // Debug, check for problems in xThermo
     // Function to compute and print global min/max for a field
auto printGlobalMinMax = [](const volScalarField& field, const std::string& fieldName)
{
    // Internal field min/max
    scalar globalMinInternal = gMin(field.internalField());
    scalar globalMaxInternal = gMax(field.internalField());

    // Boundary field min/max
    scalar localMinBoundary = VGREAT;    // Very large number as initial min
    scalar localMaxBoundary = -VGREAT;  // Very small number as initial max

    forAll(field.boundaryField(), patchI)
    {
        const fvPatchField<scalar>& patchField = field.boundaryField()[patchI];
        scalar minPatch = min(patchField);
        scalar maxPatch = max(patchField);
        localMinBoundary = min(localMinBoundary, minPatch);
        localMaxBoundary = max(localMaxBoundary, maxPatch);
    }

    // Perform global reduction for boundary min/max
    scalar globalMinBoundary = localMinBoundary;
    scalar globalMaxBoundary = localMaxBoundary;

    reduce(globalMinBoundary, minOp<scalar>());
    reduce(globalMaxBoundary, maxOp<scalar>());

    // Calculate overall global min/max including boundaries
    scalar globalMinField = min(globalMinInternal, globalMinBoundary);
    scalar globalMaxField = max(globalMaxInternal, globalMaxBoundary);

    // Print results
    Info << "Global minimum of " << fieldName << " (including boundaries): " << globalMinField << endl;
    Info << "Global maximum of " << fieldName << " (including boundaries): " << globalMaxField << endl;
};

// Calculate and print global min/max for all fields
/*printGlobalMinMax(rho, "rho");
printGlobalMinMax(mu, "mu");
printGlobalMinMax(Cp, "Cp");
printGlobalMinMax(betaT, "betaT");
printGlobalMinMax(alphaP, "alphaP");*/

}
