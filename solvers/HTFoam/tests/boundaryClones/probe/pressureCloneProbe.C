#include "fvCFD.H"
#include "noFluxFvPatchScalarField.H"
#include "HydrothermalMassFluxPressureFvPatchScalarField.H"
#include "submarinePressureFvPatchScalarField.H"
#include <type_traits>

static_assert(!std::is_copy_constructible<Foam::noFlux>::value,"Plain noFlux copy must be deleted");
static_assert(!std::is_copy_constructible<Foam::HydrothermalMassFluxPressure>::value,"Plain mass-flux copy must be deleted");
static_assert(!std::is_copy_constructible<Foam::submarinePressureFvPatchScalarField>::value,"Plain submarine copy must be deleted");

using namespace Foam;

template<class Boundary>
void checkCloning(volScalarField& p,const label patchI)
{
    p.correctBoundaryConditions();
    const fvPatchScalarField& base=p.boundaryField()[patchI];
    const auto& source=refCast<const Boundary>(base);
    volScalarField owner("owner",p);
    auto check = [&](const fvPatchScalarField& field)
    {
        if (field.type()!=source.type() || &field.internalField()!=&owner.internalField()
         || &field.patch()!=&source.patch() || gMax(mag(field-source))>1e-10
         || gMax(mag(field.snGrad()-source.snGrad()))>1e-10)
        {
            FatalErrorInFunction << "Copy reference, patch, values or gradients changed for "
                << source.type() << abort(FatalError);
        }
        OStringStream original,copied;
        source.write(original);field.write(copied);
        if (original.str()!=copied.str())
        {
            FatalErrorInFunction << "Copied configuration changed for " << source.type()
                << abort(FatalError);
        }
    };
    check(owner.boundaryField()[patchI]);
    Boundary direct(source,owner.internalField());
    check(direct);
    auto cloned=base.clone(owner.internalField());
    check(cloned());

    const scalarField originalInternal(p.primitiveField());
    const scalarField originalGradient(source.snGrad());
    owner.primitiveFieldRef() += 20;
    cloned.ref().evaluate();
    scalarField expected(source);
    if (isA<fixedGradientFvPatchScalarField>(source))
    {
        expected=cloned().patchInternalField()+originalGradient/source.patch().deltaCoeffs();
    }
    if (gMax(mag(cloned()-expected))>1e-10
     || gMax(mag(p.primitiveField()-originalInternal))>1e-10)
    {
        FatalErrorInFunction << "Clone owner/evaluation mismatch for " << source.type()
            << abort(FatalError);
    }
    Info<< "PASS " << source.type()
        << ": explicit-reference copy, clone(iF), field copy, values/gradient/configuration and owner" << endl;
}

int main(int argc,char* argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    uniformDimensionedVectorField g
    (
        IOobject("g",runTime.constant(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE)
    );
    // Synthetic, non-default lookup names exercise preservation of BC settings.
    surfaceScalarField mobility
    (
        IOobject("mobilityCloneTest",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),
        mesh,dimensionedScalar("mobility",dimTime,2)
    );
    surfaceScalarField gravityFlux
    (
        IOobject("gravityCloneTest",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),
        mesh,dimensionedScalar("gravityFlux",dimMass/dimTime,3)
    );
    volScalarField p
    (
        IOobject("p",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh
    );
    const label patchI=mesh.boundaryMesh().findPatchID("bottom");
    const word type=p.boundaryField()[patchI].type();
    if (type==noFlux::typeName) checkCloning<noFlux>(p,patchI);
    else if (type==HydrothermalMassFluxPressure::typeName) checkCloning<HydrothermalMassFluxPressure>(p,patchI);
    else if (type==submarinePressureFvPatchScalarField::typeName) checkCloning<submarinePressureFvPatchScalarField>(p,patchI);
    else FatalErrorInFunction << "Unexpected test BC " << type << abort(FatalError);
    return 0;
}
