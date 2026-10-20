// --- initpEqn.H : Hydrostatic pressure initialisation with non-orth correctors
//     - Uses PIMPLE.residualControl.p for residual stop (abs/rel)
//     - Uses INIT.maxDeltaP for property–pressure fixed-point stop
//     - OF10-safe dictionary access

// -----------------------------------------------------------------------------
// Grab fvSolution and sub-dicts (robust to legacy/new styles)
// -----------------------------------------------------------------------------
const IOdictionary& fvSol =
    mesh.thisDb().lookupObject<IOdictionary>("fvSolution");

const dictionary& pimDict = fvSol.subDict("PIMPLE");

// Read residualControl for pressure (support v5 scalar or modern sub-dict)
scalar absTolP = 1e-3;   // default absolute tol on *initial* residual
scalar relTolP = 0.0;    // default disabled (fraction of first initial residual)

if (pimDict.found("residualControl"))
{
    const dictionary& rc = pimDict.subDict("residualControl");

    if (rc.found("p"))
    {
        if (rc.isDict("p"))
        {
            // modern style:
            const dictionary& prc = rc.subDict("p");
            absTolP = prc.lookupOrDefault<scalar>("tolerance", absTolP);
            relTolP = prc.lookupOrDefault<scalar>("relTol",    relTolP);
        }
        else
        {
            // OF5 shorthand:  p 1e-4;
            absTolP = rc.lookupOrDefault<scalar>("p", absTolP);
            relTolP = 0.0;
        }
    }
}

// Read counts
const label nCorr    = pimDict.lookupOrDefault<label>("nCorrectors",              1);
const label nNonOrth = pimDict.lookupOrDefault<label>("nNonOrthogonalCorrectors", 0);

// Read physical coupling criterion from PTCOUPLING (optional)
scalar maxDeltaPcrit = GREAT;
if (fvSol.found("PTCOUPLING"))
{
    const dictionary& ptcDict = fvSol.subDict("PTCOUPLING");
    maxDeltaPcrit = ptcDict.lookupOrDefault<scalar>("maxDeltaP", maxDeltaPcrit);
}

// -----------------------------------------------------------------------------
// Driver: outer loop via pimple.loop() (bounded by nOuterCorrectors in fvSolution)
// -----------------------------------------------------------------------------
pimpleControl pimple(mesh);

// Book-keeping for PIMPLE-like relative criterion and physical change
scalar firstInitRes = -1.0;
p.storePrevIter();   // so p.prevIter() is defined

bool initConverged = false;

while (pimple.loop())
{
    // --- assemble coeffs/properties for this outer iteration
    #include "updateProps.H"
    fvModels.correct();

    // Coeffs for Darcy system
    volScalarField rAU(permeability/mu); // K/mu
    surfaceScalarField rhorAUf("rhorAUf", fvc::interpolate(rho*rAU));
    volVectorField   HbyA(U*0);
    surfaceScalarField phig("phig", (fvc::interpolate(rho)*rhorAUf * g) & mesh.Sf());
    surfaceScalarField phiHbyA("phiHbyA", phig);

    // keep BCs consistent with flux
    constrainPressure(p, rho, U, phiHbyA, rhorAUf);

    // --- inner pressure correctors (often 1 for Darcy init)
    const label nCorrEff = (nCorr > 0) ? nCorr : 1;
        scalar initResRecorded = GREAT;

    for (label corr = 0; corr < nCorrEff; ++corr)
    {
        // --- non-orthogonal correctors
        for (label nonOrth = 0; nonOrth <= nNonOrth; ++nonOrth)
        {
            fvScalarMatrix pEqn
            (
                // div( (rho*K/mu) * rho*g ) - laplacian( (rho*K/mu), p ) = 0
                fvc::div(phiHbyA) - fvm::laplacian(rhorAUf, p)
            );

            fvConstraints.constrain(pEqn);

            // Solve each pass; use the *final* non-orth residual for convergence
            pEqn.relax(); 
            const Foam::SolverPerformance<scalar> sp = pEqn.solve();

            if (nonOrth == nNonOrth)
            {
                initResRecorded = sp.initialResidual();

                // Accept solution: update flux & Darcy velocity once per corrector
                phi = phiHbyA + pEqn.flux();

                U = HbyA + rAU * fvc::reconstruct((phig + pEqn.flux())/rhorAUf);
                U.correctBoundaryConditions();
                fvConstraints.constrain(U);
            }
        }

        // Couple properties once per corrector (not every non-orth)
        #include "updateProps.H"
        fvModels.correct();
    }

    // --- Convergence checks (pressure residual + physical coupling)
    if (firstInitRes < 0) firstInitRes = initResRecorded;

    const bool absOK = (initResRecorded < absTolP);
    const bool relOK = (relTolP > 0 && initResRecorded <= relTolP*firstInitRes);

        tmp<volScalarField> tDeltaP = mag(p - p.prevIter());
        const scalar maxDeltaP = gMax(tDeltaP());
    const bool physOK = (maxDeltaP < maxDeltaPcrit);

    Info<< "initpEqn: initRes=" << initResRecorded
        << " (first=" << firstInitRes << ")"
        << ", max|delta p|=" << maxDeltaP
            << " -> absOK=" << absOK
            << ", relOK=" << relOK
        << ", physOK=" << physOK << nl;

    // prepare for next outer iteration if any
        p.storePrevIter();

    if (physOK)
        {
        initConverged = true;
        break;  // exit outer pimple.loop()
    }
}

// Optionally report if we simply hit nOuterCorrectors
if (!initConverged)
{
    Info<< "initpEqn: reached nOuterCorrectors with initRes="
        << (firstInitRes >= 0 ? firstInitRes : -1)
        << " (set tighter/looser PIMPLE.residualControl.p or INIT.maxDeltaP if needed)" << nl;
}
