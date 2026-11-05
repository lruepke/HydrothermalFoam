// Reference kr is independent of T. Create a valid derived coefficient before
// constructing temperature patches; never read kr_eff back as input on restart.
const dimensionSet conductivityDimensions(1, 1, -3, -1, 0, 0, 0);
const word krSource(transportProperties.lookupOrDefault<word>("krSource", "uniform"));
autoPtr<volScalarField> krReference;
if (krSource == "uniform")
{
    const dimensionedScalar uniformKr(transportProperties.lookup("kr"));
    krReference.reset
    (
        new volScalarField
        (
            IOobject("kr", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::NO_WRITE),
            mesh, uniformKr, "zeroGradient"
        )
    );
}
else if (krSource == "field")
{
    krReference.reset
    (
        new volScalarField
        (
            IOobject("kr", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE),
            mesh
        )
    );
}
else
{
    FatalErrorInFunction << "Unknown krSource=" << krSource
        << "; expected uniform or field in constant/transportProperties"
        << abort(FatalError);
}
volScalarField& kr = krReference();
Info<< "Conductivity reference: krSource=" << krSource
    << "; temperature coefficient: kr_eff; scheme: laplacian(kr,T)" << endl;

// Calculated physical patches store derived face values, not another independent
// set of conductivity boundary laws. Mesh constraint patches remain standard.
volScalarField kr_eff
(
    IOobject("kr_eff", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    mesh, dimensionedScalar("kr_eff", conductivityDimensions, 0)
);

// Shared by startup and pre-assembly refresh; errors avoid collective geometry.
auto checkConductivity = [&](const volScalarField& field)
{
    if (field.dimensions() != conductivityDimensions)
    {
        FatalErrorInFunction << "Conductivity " << field.name() << " has dimensions "
            << field.dimensions() << "; require " << conductivityDimensions
            << ", time=" << runTime.timeName() << ", rank=" << Pstream::myProcNo()
            << abort(FatalError);
    }
    auto checkValue = [&](const scalar value, const label cellI,
                          const label patchI, const label faceI)
    {
        if (!std::isfinite(value) || value <= 0)
        {
            OStringStream context;
            context.precision(17);
            context << "Invalid conductivity " << field.name() << '=' << value
                << " W/(m K); require finite and > 0; time=" << runTime.timeName()
                << ", rank=" << Pstream::myProcNo();
            if (cellI >= 0)
            {
                context << ", local cell=" << cellI
                    << ", centre=" << mesh.cellCentres()[cellI];
            }
            if (patchI >= 0)
            {
                const fvPatch& patch = mesh.boundary()[patchI];
                context << ", patch=" << patch.name() << ", local face=" << faceI
                    << ", centre=" << mesh.faceCentres()[patch.start() + faceI];
            }
            FatalErrorInFunction << context.str().c_str() << abort(FatalError);
        }
    };
    forAll(field, cellI) checkValue(field[cellI], cellI, -1, -1);
    forAll(field.boundaryField(), patchI)
    {
        forAll(field.boundaryField()[patchI], faceI)
        {
            checkValue(field.boundaryField()[patchI][faceI], -1, patchI, faceI);
        }
    }
};
#include "updateConductivity.H"
