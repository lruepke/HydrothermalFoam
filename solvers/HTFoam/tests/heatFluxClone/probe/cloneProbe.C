#include "fvCFD.H"
#include "HydrothermalHeatFluxFvPatchScalarField.H"
#include <type_traits>

static_assert
(
    !std::is_copy_constructible<Foam::HydrothermalHeatFlux>::value,
    "OpenFOAM 10 requires an explicit internal-field reference when copying"
);

int main(int argc, char* argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    IOdictionary legacy
    (
        IOobject("thermophysicalProperties", runTime.constant(), mesh,
                 IOobject::MUST_READ, IOobject::NO_WRITE)
    );
    volScalarField conductivity
    (
        IOobject("kr_eff", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE), mesh
    );
    volScalarField T
    (
        IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE), mesh
    );
    T.correctBoundaryConditions();
    const label patchI=mesh.boundaryMesh().findPatchID("bottom");
    const fvPatchScalarField& base=T.boundaryField()[patchI];
    const HydrothermalHeatFlux& source=refCast<const HydrothermalHeatFlux>(base);
    volScalarField owner("owner",T); // Ordinary field copying must use clone(iF).

    auto check = [&](const fvPatchScalarField& field)
    {
        const auto& copy=refCast<const HydrothermalHeatFlux>(field);
        if (&copy.internalField()!=&owner.internalField()
         || &copy.patch()!=&source.patch()
         || gMax(mag(copy-source))>1e-12
         || gMax(mag(copy.gradient()-source.gradient()))>1e-12)
        {
            FatalErrorInFunction << "Cloned field reference, patch, value or gradient mismatch"
                << abort(FatalError);
        }
        OStringStream original,cloned;
        source.write(original);
        copy.write(cloned);
        if (original.str()!=cloned.str())
        {
            FatalErrorInFunction << "Cloned boundary configuration changed" << abort(FatalError);
        }
    };
    check(owner.boundaryField()[patchI]);
    HydrothermalHeatFlux direct(source,owner.internalField());
    check(direct);
    auto cloned=base.clone(owner.internalField());
    check(cloned());

    // Check that the clone actually evaluates against its new owner's cells.
    owner.primitiveFieldRef() += 20;
    cloned.ref().evaluate();
    const scalarField expected
    (
        cloned().patchInternalField()+source.gradient()/mesh.boundary()[patchI].deltaCoeffs()
    );
    if (gMax(mag(cloned()-expected))>1e-12
     || gMax(mag(T.primitiveField()-scalar(300)))>1e-12)
    {
        FatalErrorInFunction << "Clone used the wrong internal-field owner" << abort(FatalError);
    }
    Info<< "PASS field copy, explicit-reference constructor, clone(iF), configuration and owner evaluation" << endl;
    return 0;
}
