/**
 * @file pEqn.H
 * author Lars Ruepke and Zhikui Guo
 * @brief Pressure equation with optional time-derivative coupling and non-orthogonal correction
 *
 * \f[
 * \phi\, \rho_f \left(\beta_T \frac{\partial p}{\partial t} - \alpha_P \frac{\partial T}{\partial t}\right)
 * = \nabla \cdot\left(\rho_f \frac{k}{\mu_f}\left(\nabla p - \rho_f \mathbf{g}\right)\right)
 * \f]
 */

{
    // Mobility etc.
    volScalarField rAU(permeability/mu); // K/mu
    surfaceScalarField rhorAUf("rhorAUf", fvc::interpolate(rho*rAU));
    volVectorField HbyA(U*0);

    // Gravity head flux on faces
    surfaceScalarField phig
    (
        "phig",
        (fvc::interpolate(rho)*rhorAUf * g) & mesh.Sf()
    );

    surfaceScalarField phiHbyA("phiHbyA", phig);

    // Keep pressure BCs consistent with the flux
    constrainPressure(p, rho, U, phiHbyA, rhorAUf);

    // Explicit transient terms (your original form)
    fvScalarMatrix p_rghDDtEqn
    (
        porosity*rho*betaT*fvm::ddt(p)       // implicit in p
      - porosity*rho*alphaP*fvc::ddt(T)      // explicit in T
      + fvc::div(phiHbyA)
        ==
        porosity*betaT*rho*fvModels.source(p)
    );

    // ---- Non-orthogonal correctors (driven by __nNonOrth from the main loop) ----
    for (label nonOrth = 0; nonOrth <= __nNonOrth; ++nonOrth)
    {
        fvScalarMatrix pEqn
        (
            p_rghDDtEqn
          - fvm::laplacian(rhorAUf, p)
        );

        fvConstraints.constrain(pEqn);

        // Equation under-relaxation follows relaxationFactors.equations{ p ... }
        // (Set to 1.0 in fvSolution if you want it effectively off.)
        pEqn.relax();

        // Keep using your "p" solver entry (minimal change)
        const Foam::SolverPerformance<scalar> sp = pEqn.solve("p");
        //pEqn.solve("p");

        // On the final non-orth pass, accept solution and update flux/velocity
        if (nonOrth == __nNonOrth)
        {
            __initResP = sp.initialResidual();     // <<< expose to the monitor
            phi = phiHbyA + pEqn.flux();

            U = HbyA + rAU*fvc::reconstruct((phig + pEqn.flux())/rhorAUf);
            U.correctBoundaryConditions();
            fvConstraints.constrain(U);
        }
    }
}

// #include "rhoEqn.H"
// #include "compressibleContinuityErrs.H"
