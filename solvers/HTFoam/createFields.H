#include "createxThermo.H"

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

// read properties
#include <readTransportProperties.H>

props = pxThermo->UpdateState_TPX(278.15, 1E6, constX);
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
        dimensionedScalar("rho",dimensionSet(1,-3,0,0,0,0,0),props.Rho)
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
        dimensionedScalar("mu",dimensionSet(1,-1,-1,0,0,0,0),props.Mu_l)
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
        dimensionedScalar("Cp",dimensionSet(0,2,-2,-1,0,0,0),props.Cp)
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
        dimensionedScalar("alphaP",dimensionSet(0,0,0,-1,0,0,0),props.IsobaricExpansivity)
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
        dimensionedScalar("betaT",dimensionSet(-1,1,2,0,0,0,0),props.IsothermalCompressibility)
    );

#include "updateProps.H"    

#include "readGravitationalAcceleration.H"

#include "compressibleCreatePhi.H"
#include "createFvModels.H"
#include "createFvConstraints.H"

