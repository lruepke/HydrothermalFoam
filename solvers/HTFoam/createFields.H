#include "createxThermo.H"
#include "readTransportProperties.H"
#include "createConductivity.H"

// pressure
    volScalarField p
    (
        IOobject
        (
            "p",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );
// Temperature field
    Info<< "Reading field T\n" << endl;
    volScalarField T
    (
        IOobject
        (
            "T",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );

// Darcy Velocity
    volVectorField U
    (
        IOobject
        (
            "U",
            runTime.timeName(),
            mesh,
            IOobject::READ_IF_PRESENT,
            IOobject::AUTO_WRITE
        ),
        mesh,
        dimensionedVector("U",dimensionSet(0,1,-1,0,0,0,0),Foam::vector::zero)
    );
// Permeability
    Info<< "Reading permeability \n"<<endl;
    volScalarField permeability
    (
        IOobject
        (
            "permeability",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );

// Static permeability still needs current neighbour values on coupled patches.
// Refresh after every read, including restarts, before constructing mobility.
permeability.correctBoundaryConditions();

// This BC needs only T's internal values and kr_eff. Other T patches can need
// phi, which does not exist yet: defer their normal evaluation until assembly.
// Do this on restarts too, rather than trusting saved gradients/placeholder values.
forAll(T.boundaryField(), patchI)
{
    if (T.boundaryField()[patchI].type() == "hydrothermalHeatFlux")
    {
        T.boundaryFieldRef()[patchI].evaluate();
    }
}

// Temporary dimensioned storage only: updateProps.H fills every active value
// from the actual case state before gravity/flux construction or equation use.
// Fluid density
    Info<< "update fluid density \n" << endl;
    volScalarField rho
    (
        IOobject
        (
            "rho",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        mesh,
        dimensionedScalar("rho",dimensionSet(1,-3,0,0,0,0,0),0.0)
    );
// fluid dynamic viscosity
    volScalarField mu
    (
        IOobject
        (
            "mu",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        mesh,
        dimensionedScalar("mu",dimensionSet(1,-1,-1,0,0,0,0),0.0)
    );


//  specific heat of fluid
    volScalarField Cp
    (
        IOobject
        (
            "Cp",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh,
        dimensionedScalar("Cp",dimensionSet(0,2,-2,-1,0,0,0),0.0)
    );
//  thermal expansivity
    volScalarField alphaP
    (
        IOobject
        (
            "alphaP",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh,
        dimensionedScalar("alphaP",dimensionSet(0,0,0,-1,0,0,0),0.0)
    );
//  compresibility
    volScalarField betaT
    (
        IOobject
        (
            "betaT",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh,
        dimensionedScalar("betaT",dimensionSet(-1,1,2,0,0,0,0),0.0)
    );

#include "updateProps.H"    

#include "readGravitationalAcceleration.H"

#include "compressibleCreatePhi.H"
#include "createFvModels.H"
#include "createFvConstraints.H"

