
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
// Conductivity input and derived field are created before T (see createFields.H).
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
