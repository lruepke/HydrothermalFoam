scalar CoNum_por = 0.0;
scalar meanCoNum_por = 0.0;

if (mesh.nInternalFaces())
{
    scalarField sumPhi
        (
            fvc::surfaceSum(mag(phi))().internalField()
        );

    CoNum_por = 0.5*gMax(sumPhi/mesh.V().field())*runTime.deltaTValue();

    meanCoNum_por = 
        0.5*(gSum(sumPhi)/gSum(mesh.V().field()))*runTime.deltaTValue();

}

Info<< "Porous Courant Number mean: " << meanCoNum_por << ", max: " << CoNum_por << endl;
