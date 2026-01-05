/**
 * @file TEqn.H
 * @brief Temperature equation (used inside mini Picard loop, after pEqn.H)
 *
 * \f[
 * \big(\phi\,\rho_f c_{pf} + (1-\phi)\,\rho_r c_{pr}\big)\,\frac{\partial T}{\partial t}
 * = \nabla\cdot(\lambda_r \nabla T) - \rho_f c_{pf}\,\mathbf{v}\cdot\nabla T
 *   + \frac{\mu_f}{k}\,|\mathbf{v}|^2
 *   - \left(\frac{\partial\ln\rho}{\partial\ln T}\right)_p \frac{Dp}{Dt}
 * \f]
 */

{
    fvScalarMatrix TEqn
    (
        // transient capacity (fluid + rock matrix)
        (porosity*rho*Cp + (1.0 - porosity)*rho_rock*cp_rock) * fvm::ddt(T)

      // advection with variable Cp  (phi was just updated by pEqn.H)
      + fvm::div( phi * fvc::interpolate(Cp), T )

      ==
        // conduction
        fvm::laplacian(kr, T)

      // product-rule correction for variable Cp in advection (implicit sink/source)
      + fvm::Sp( fvc::div( phi * fvc::interpolate(Cp) ), T )

      // viscous/drag dissipation (Darcy)
      + mu/permeability * magSqr(U)

      // thermoelastic/compressibility coupling term
      + fvm::Sp( alphaP*( porosity*fvc::ddt(p) + (U & fvc::grad(p)) ), T )

        // add any additional volumetric sources via fvModels if you use them elsewhere:
        // + fvModels.source(T)   // uncomment if applicable in your code base
    );

    // Apply constraints & relaxation consistent with fvSolution
    fvConstraints.constrain(TEqn);
    TEqn.relax();              // set relaxationFactors.equations{ T 1.0; } to disable

    // Solve (simple: use "T" entry; switch to "TFinal" in the last Picard iter if desired)
    const Foam::SolverPerformance<scalar> spT = TEqn.solve("T");
    //TEqn.solve("T");
    __initResT = spT.initialResidual();                  // <<< expose to the monitor

    fvConstraints.constrain(T);
    T.correctBoundaryConditions();
}
