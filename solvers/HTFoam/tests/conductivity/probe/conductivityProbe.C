// Exercise the production conductivity updater and runtime BC independently of
// flow/EOS coupling. This is a test executable, not another production solver.
#include "fvCFD.H"
#include <cmath>
#include <limits>

int main(int argc, char* argv[])
{
    argList::addBoolOption("nan", "Inject a nonfinite reference cell to test fail-fast validation");
    argList::addBoolOption("solve", "Solve steady conduction with zero source");
    argList::addBoolOption("cycle", "Double reference values and refresh within the same timestep");
    argList::addBoolOption("legacy", "Register thermophysicalProperties for legacy BC checks");
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    IOdictionary transportProperties
    (
        IOobject("transportProperties", runTime.constant(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE)
    );
    autoPtr<IOdictionary> legacy;
    if (args.optionFound("legacy"))
    {
        legacy.reset(new IOdictionary
        (
            IOobject("thermophysicalProperties", runTime.constant(), mesh,
                     IOobject::MUST_READ, IOobject::NO_WRITE)
        ));
    }
    #include "createConductivity.H"
    volScalarField T
    (
        IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE), mesh
    );
    auto report = [&](const word& suffix)
    {
        T.correctBoundaryConditions();
        OFstream out(runTime.path()/fileName("patch-" + suffix + ".txt"));
        out.precision(17);
        forAll(T.boundaryField(), patchI)
        {
            const fvPatch& patch = mesh.boundary()[patchI];
            const scalarField gradient
            (
                patch.coupled()
              ? T.boundaryField()[patchI].snGrad(patch.deltaCoeffs())
              : T.boundaryField()[patchI].snGrad()
            );
            forAll(T.boundaryField()[patchI], faceI)
            {
                const vector& centre = patch.Cf()[faceI];
                out << patch.name() << ' ' << faceI << ' '
                    << centre.x() << ' ' << centre.y() << ' ' << centre.z() << ' '
                    << kr_eff.boundaryField()[patchI][faceI] << ' ' << gradient[faceI]
                    << ' ' << T.boundaryField()[patchI][faceI]
                    << ' ' << patch.magSf()[faceI] << nl;
            }
        }
    };
    if (args.optionFound("nan"))
    {
        kr[0] = std::numeric_limits<scalar>::quiet_NaN();
        #include "updateConductivity.H"
    }
    report("initial");
    if (args.optionFound("solve"))
    {
        mesh.schemes().setFluxRequired(T.name());
        fvScalarMatrix equation(-fvm::laplacian(kr_eff, T, "laplacian(kr,T)"));
        equation.solve();
        report("solved");
        surfaceScalarField flux("conductiveFlux", equation.flux());
        OFstream out(runTime.path()/"face-flux.txt");
        out.precision(17);
        forAll(flux, faceI) out << faceI << ' ' << flux[faceI] << nl;
        OFstream cells(runTime.path()/"cells.txt");
        cells.precision(17);
        forAll(T, cellI) cells << mesh.C()[cellI].y() << ' ' << T[cellI] << ' ' << kr_eff[cellI] << nl;
    }
    if (args.optionFound("cycle"))
    {
        kr.primitiveFieldRef() *= 2;
        forAll(kr.boundaryField(), patchI)
        {
            if (!mesh.boundary()[patchI].coupled())
            {
                kr.boundaryFieldRef()[patchI] == scalarField(2*kr.boundaryField()[patchI]);
            }
        }
        #include "updateConductivity.H"
        report("doubled");
    }
    T.write(); // Exercise BC serialization in this disposable test case.
    Info<< "End" << endl;
    return 0;
}
