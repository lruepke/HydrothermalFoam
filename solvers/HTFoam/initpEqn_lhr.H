/**
 * @file initpEqn.H
 * @author Zhikui Guo (zhikuiguo@live.cn)
 * @brief Calculate initial hydrostatic pressure.
 * 
 * \f[ \nabla  \cdot \left( {{\rho _f}\frac{k}{{{\mu _f}}}\left( {\nabla p - {\rho _f}\vec{g}} \right)} \right)=0 \f]
 * @version 1.0
 * @date 2019-10-14
 * 
 * @copyright Copyright (c) 2019
 * 
 */
{
    
while (pimple.loop())  // Loop until fvSolution's convergence criteria are met
{
    #include "updateProps.H"
    fvModels.correct();

    volScalarField rAU(permeability/mu); //K/mu
    surfaceScalarField rhorAUf("rhorAUf", fvc::interpolate(rho*rAU));//rho/A on surface
    volVectorField HbyA(U*0);

    surfaceScalarField phig("phig",(fvc::interpolate(rho)*rhorAUf * g) & mesh.Sf());

    surfaceScalarField phiHbyA
    (
        "phiHbyA",
        phig
    );

    //Info << "phiHbyA max: " << gMax(mag(phiHbyA)) 
    //    << ", rhorAUf max: " << gMax(mag(rhorAUf)) << endl;

    // Update the pressure BCs to ensure flux consistency
    //Info << "p before constrainPressure: min = " << gMin(p) 
    //    << ", max = " << gMax(p) << endl;
    constrainPressure(p, rho, U, phiHbyA, rhorAUf);
    //Info << "p after constrainPressure: min = " << gMin(p) 
    //    << ", max = " << gMax(p) << endl;            
        
    //Info << "Pimple loop" << endl;

    while (pimple.correctNonOrthogonal())
    {
        // Define the heat conduction equation with source term
        fvScalarMatrix pEqn
        (
            fvc::div(phiHbyA) - fvm::laplacian(rhorAUf, p)
        );

        fvConstraints.constrain(pEqn);
        //pEqn.relax();
        pEqn.solve();

        //fvConstraints.constrain(T);
        //Info << "non-orthogobal loop" << endl;

        if (pimple.finalNonOrthogonalIter())
        {
            // option 1: calculate velocity using Darcy's law directly
            // U=-permeability/mu*(fvc::grad(p)-rho*g);

            // option 2: using flux reconstruct velocity
            phi = phiHbyA + pEqn.flux();

            U = HbyA + rAU*fvc::reconstruct((phig + pEqn.flux())/rhorAUf);
            U.correctBoundaryConditions();
            fvConstraints.constrain(U);  // after velocity update
            // Now check residual and break if converged

        }
    }

}
}