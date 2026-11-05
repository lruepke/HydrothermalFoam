// Explicit steady Darcy pressure initialization. No solutionControl state is owned.
const dictionary& fvSol = mesh.solution().dict();
const dictionary& pimDict = fvSol.subDict("PIMPLE");
const dictionary initDict(fvSol.subOrEmptyDict("INIT"));
const dictionary ptcDict(fvSol.subOrEmptyDict("PTCOUPLING"));

const label maxInitIters = initDict.lookupOrDefault<label>
(
    "maxIterations", pimDict.lookupOrDefault<label>("nOuterCorrectors", 1)
);
const label nCorr = initDict.lookupOrDefault<label>
(
    "nCorrectors", pimDict.lookupOrDefault<label>("nCorrectors", 1)
);
const label nNonOrth = pimDict.lookupOrDefault<label>
(
    "nNonOrthogonalCorrectors", 0
);
const bool enabled = initDict.lookupOrDefault<bool>("enabled", true);
const bool checkDeltaP = initDict.found("maxDeltaP") || ptcDict.found("maxDeltaP");
const scalar maxDeltaPcrit = initDict.lookupOrDefault<scalar>
(
    "maxDeltaP", ptcDict.lookupOrDefault<scalar>("maxDeltaP", GREAT)
);
if (maxInitIters < 0 || nNonOrth < 0 || nCorr < 0
 || !std::isfinite(maxDeltaPcrit) || maxDeltaPcrit < 0)
{
    FatalErrorInFunction << "Invalid initialization controls: require nonnegative "
        << "counts and finite nonnegative maxDeltaP" << exit(FatalError);
}
if (ptcDict.found("maxInitOuterIters"))
{
    WarningInFunction << "PTCOUPLING.maxInitOuterIters remains unused. Use "
        << "INIT.maxIterations; fallback is PIMPLE.nOuterCorrectors." << nl;
}
if (pimDict.found("residualControl") || pimDict.found("outerCorrectorResidualControl"))
{
    Info<< "initpEqn: PIMPLE residual controls do not govern initialization; "
        << "linear tolerances remain in solvers.p." << nl;
}

bool initConverged = false;
label initIters = 0;
scalar maxDeltaP = GREAT;
Info<< "initpEqn: enabled=" << enabled << ", maxIterations=" << maxInitIters
    << ", pressureCorrectors=" << max(nCorr, label(1))
    << ", nonOrthogonalCorrectors=" << nNonOrth
    << ", pressureChangeCheck=" << checkDeltaP << nl;

for (label outer = 0; enabled && outer < maxInitIters; ++outer)
{
    ++initIters;
    const volScalarField pBefore("pBeforeInit", p);
    const volScalarField rhoBefore("rhoBeforeInit", rho);
    const volScalarField muBefore("muBeforeInit", mu);
    scalar initResRecorded = GREAT;
    scalar finalResRecorded = GREAT;

    // Startup supplies EOS properties; subsequent iterations use the EOS update
    // at the end of the previous outer iteration. Freeze this coefficient
    // snapshot across all inner pressure and non-orthogonal correctors.
    fvModels.correct();
    volScalarField rAU(permeability/mu);
    surfaceScalarField rhorAUf("rhorAUf", fvc::interpolate(rho*rAU));
    surfaceScalarField phig("phig", (fvc::interpolate(rho)*rhorAUf*g) & mesh.Sf());
    surfaceScalarField phiHbyA("phiHbyA", phig);
    constrainPressure(p, rho, U, phiHbyA, rhorAUf);

    for (label corr = 0; corr < max(nCorr, label(1)); ++corr)
    {
        for (label nonOrth = 0; nonOrth <= nNonOrth; ++nonOrth)
        {
            fvScalarMatrix pEqn
            (
                fvc::div(phiHbyA) - fvm::laplacian(rhorAUf, p)
            );
            fvConstraints.constrain(pEqn);
            pEqn.relax();
            const Foam::SolverPerformance<scalar> sp = pEqn.solve();
            if (nonOrth == nNonOrth)
            {
                initResRecorded = sp.initialResidual();
                finalResRecorded = sp.finalResidual();
                phi = phiHbyA + pEqn.flux();
                U = fvc::reconstruct(phi)/rho;
                U.correctBoundaryConditions();
                fvConstraints.constrain(U);
            }
        }
    }

    // One EOS evaluation per outer iteration, for diagnostics and the next
    // coefficient snapshot. No physical coefficient updates inside either loop.
    #include "updateProps.H"
    fvModels.correct();

    maxDeltaP = gMax(mag(p - pBefore)());
    const scalar maxRelDeltaRho = gMax(mag((rho - rhoBefore)/rhoBefore)());
    // Permeability is fixed during initialization: relative mobility change.
    const scalar maxRelDeltaMobility = gMax(mag(muBefore/mu - scalar(1))());
    const scalar maxMassImbalance = gMax(mag(fvc::div(phi))());
    initConverged = checkDeltaP && maxDeltaP < maxDeltaPcrit;
    Info<< "initpEqn: iteration=" << initIters << ", initRes=" << initResRecorded
        << ", finalRes=" << finalResRecorded << ", max|delta p|=" << maxDeltaP
        << ", maxRelDeltaRho=" << maxRelDeltaRho
        << ", maxRelDeltaMobility=" << maxRelDeltaMobility
        << ", max|div(phi)|=" << maxMassImbalance << " kg/m3/s"
        << ", pressureChangeOK=" << initConverged << nl;
    if (initConverged) break;
}
if (!enabled || maxInitIters == 0)
{
    Info<< "initpEqn: skipped by initialization controls" << nl;
}
else if (!initConverged)
{
    WarningInFunction << "Initialization iteration budget exhausted after "
        << initIters << " iterations; max|delta p|=" << maxDeltaP
        << ". " << (checkDeltaP ? "Pressure-change target not met. "
                               : "No pressure-change target configured. ")
        << "Continuing with the current fields; inspect property changes and "
        << "mass imbalance. Residuals alone do not establish EOS consistency." << nl;
}
else
{
    Info<< "initpEqn: pressure-change target met after " << initIters
        << " iterations; property changes and mass imbalance are diagnostic only." << nl;
}
