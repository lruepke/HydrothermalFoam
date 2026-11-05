// Constant-property, zero-gravity Darcy verification; never builds HTFoam.
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    volScalarField p
    (
        IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE),
        mesh
    );
    volScalarField permeability
    (
        IOobject("permeability", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE),
        mesh
    );
    volScalarField rho
    (
        IOobject("rho", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::NO_WRITE),
        mesh, dimensionedScalar("rho", dimDensity, 1000), "zeroGradient"
    );
    volScalarField mu
    (
        IOobject("mu", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::NO_WRITE),
        mesh, dimensionedScalar("mu", dimensionSet(1,-1,-1,0,0,0,0), 1e-3),
        "zeroGradient"
    );
    rho.correctBoundaryConditions();
    mu.correctBoundaryConditions();
    permeability.correctBoundaryConditions();

    // Same expression construction and face interpolation as both HTFoam p loops.
    volScalarField rAU(permeability/mu);
    tmp<volScalarField> mobility = rho*rAU;
    const word lookupKey("interpolate(" + mobility().name() + ')');
    surfaceScalarField rhorAUf("rhorAUf", fvc::interpolate(mobility));
    fvScalarMatrix equation(-fvm::laplacian(rhorAUf, p));
    equation.solve("p");
    surfaceScalarField massFlux("massFlux", equation.flux());
    volVectorField U("U", fvc::reconstruct(massFlux)/rho);

    const scalar kLow = 1e-15, kHigh = 1e-14;
    const scalar resistance = 1900/kLow + 1100/kHigh;
    const scalar qExact = 1e6/(1e-3*resistance);
    auto exactPressure = [&](scalar x)
    {
        return 31e6 - 1e6*(min(x, scalar(1900))/kLow
            + max(x-1900, scalar(0))/kHigh)/resistance;
    };
    scalar maxPressureError = 0, maxFluxError = 0, minQ = GREAT, maxQ = -GREAT;
    scalar maxVelocityError = 0;
    scalar qInterface = 0, kInterface = 0, pressureDrop = 0, exactDrop = 0;
    label interfaceCount = 0;
    forAll(p, cellI)
    {
        maxPressureError = max(maxPressureError, mag(p[cellI]-exactPressure(mesh.C()[cellI].x())));
        maxVelocityError = max(maxVelocityError, mag(U[cellI]-vector(qExact, 0, 0))/qExact);
    }
    forAll(mesh.neighbour(), faceI)
    {
        const label owner = mesh.owner()[faceI], neighbour = mesh.neighbour()[faceI];
        const scalar q = massFlux[faceI]/(1000*mesh.Sf()[faceI].x());
        minQ = min(minQ, q);
        maxQ = max(maxQ, q);
        maxFluxError = max(maxFluxError, mag(q/qExact-1));
        const label left = mesh.C()[owner].x() < mesh.C()[neighbour].x() ? owner : neighbour;
        const label right = left == owner ? neighbour : owner;
        if (mesh.C()[left].x() < 1900 && mesh.C()[right].x() > 1900)
        {
            ++interfaceCount;
            qInterface = q;
            kInterface = rhorAUf[faceI]*1e-3/1000;
            pressureDrop = p[left]-p[right];
            exactDrop = exactPressure(mesh.C()[left].x())-exactPressure(mesh.C()[right].x());
        }
    }
    if (interfaceCount != 1)
    {
        FatalErrorInFunction << "Expected one interface face" << exit(FatalError);
    }
    scalar netBoundaryMass = 0;
    forAll(massFlux.boundaryField(), patchI)
    {
        netBoundaryMass += sum(massFlux.boundaryField()[patchI]);
    }
    Info().precision(17);
    Info<< "MOBILITY_LOOKUP " << lookupKey << nl
        << "RESULT " << mesh.nCells() << ' ' << qExact << ' ' << qInterface << ' '
        << kInterface << ' ' << pressureDrop << ' ' << exactDrop << ' '
        << maxPressureError << ' ' << maxFluxError << ' '
        << (maxQ-minQ)/qExact << ' ' << netBoundaryMass << ' ' << maxVelocityError << nl;
    return 0;
}
