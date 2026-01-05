
    Info<< "Reading transportProperties\n" << endl;
    IOdictionary transportProperties
    (
        IOobject
        (
            "transportProperties",
            runTime.constant(),
            mesh,
            IOobject::MUST_READ_IF_MODIFIED,
            IOobject::NO_WRITE
        )
    );
// thermal conductivity of rock
    dimensionedScalar kr 
    (
        transportProperties.lookup("kr")
    );
// density of rock
    dimensionedScalar rho_rock 
    (
        transportProperties.lookup("rho_rock")
    );
// specific heat of rock
    dimensionedScalar cp_rock 
    (
        transportProperties.lookup("cp_rock")
    );
// porosity
    dimensionedScalar porosity 
    (
        transportProperties.lookup("porosity")
    );