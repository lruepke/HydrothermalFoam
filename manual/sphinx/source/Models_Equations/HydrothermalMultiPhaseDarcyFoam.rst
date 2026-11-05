.. _HydrothermalMultiPhaseDarcyFoam:

.. include:: /include.rst_

.. _model_multiphase_darcy:

======================================
Multiphase Darcy flow model
======================================


Pure water 
=======================

Governing equations
---------------------

The subscript of :math:`l, v` in the governing equations denote **pure liquid** phase and **pure vapour** phase, or **liquid-like superfluid** and **vapour-like superfluid**, respectively.
And all symbols are defined in :numref:`tab:symbols:multiphase`.


1. Darcy's Law

.. math::
    :label: eq:darcy:multiphase

    \vec{U_i} = - k \frac{k_{ri}}{\mu_i} (\nabla p -\rho_i \vec{g}), i = \{v, l\}
    
2. Conservation of fluid mass

.. math::
    :label: eq:conti:multiphase
    
     \frac{\partial ( \varepsilon ( S_l\rho_l + S_v \rho_v) )}{\partial t} = - \nabla \cdot (\vec{U_l} \rho_l) - \nabla \cdot (\vec{U_v} \rho_v) - \nabla \cdot (\vec{U_s} \rho_s) + Q_{H_2O}

The relation of saturation of each phase is :math:`S_l + S_v =1`. 

3. Conservation of energy 

.. math::
    :label: eq:temperature:multiphase
    
    \frac{\partial E}{\partial t}  = & \frac{\partial [\varepsilon ( S_l \rho_l h_l + S_v \rho_v h_v + S_s \rho_s h_s) + (1-\varepsilon)\rho_r C_{pr} T]}{\partial t} \\ 
    = & \nabla \cdot (\lambda_r \nabla T) - \nabla \cdot (\rho_l \vec{U_l} h_l) - \nabla \cdot (\rho_v \vec{U_v} h_v) - \nabla \cdot (\rho_s \vec{U_s} h_s) + \\
    & \frac{\mu_f}{k} \parallel \vec{U} \parallel ^2 - \left( \frac{\partial ln \rho_f}{\partial ln T} \right)_p \frac{Dp}{Dt}

Implementation 
-------------------

Pressure equation
^^^^^^^^^^^^^^^^^^^^^^

Subtituting equation :eq:`eq:darcy:multiphase` into equation :eq:`eq:conti:multiphase`, we can get the pressure equation,

.. math::
  :label: eq:pressure:multiphase

  \frac{\partial ( \varepsilon \rho_f )}{\partial t} = \nabla \cdot \left[( {\color{red}{\rho_l k \frac{k_{rl}}{\mu_l}}} +  {\color{red}{ \rho_v k \frac{k_{rv}}{\mu_v}}}) \nabla p \right] - \nabla \cdot \left[({\color{blue}{\rho_l^2 k \frac{k_{rl}}{\mu_l}}} + {\color{blue}{\rho_v^2 k \frac{k_{rv}}{\mu_v}}}) \vec{g} \right]+ Q_{H_2O} 

To simplify the formulation, we define phase mobility :math:`M_i` and gravitational contribution :math:`L_i` as follows:

.. math::
  :label: eq:MiLi

  M_i &= {\color{red}{\rho_i k \frac{k_{ri}}{\mu_i}}} \\
  L_i &= {\color{blue}{\rho_i^2 k \frac{k_{ri}}{\mu_i}}}

we can define two kinds of flux on each face of the compputational grid:

.. math::
  :label: eq:flux:multiphase

  \begin{aligned}
    \phi_p &= ( M_l + M_v) \nabla p \cdot \vec{n} \\ 
    \phi_g &= ( L_l + L_v) \vec{g} \cdot \vec{n} \\
    \phi &= \phi_p + \phi_g
  \end{aligned}

and the flux of liquid phase can be expressed as :eq:`eq:flux_l:flux_v` (see eq. 20 in :cite:`horgue2015open` )

.. math:: 
  :name: eq:flux_l:flux_v

  \phi_l = \frac{M_l}{M_l + M_v} \phi_p + \frac{L_l}{L_l + L_v}\phi_g \\
  \phi_v = \frac{M_v}{M_l + M_v} \phi_p + \frac{L_v}{L_l + L_v}\phi_g

In OpenFOAM, solving pressure equation of multiphase problem is similar to the single phase problem. 
:math:`\phi_p` can be reconstructed from pressure equation after solving it.
And velocity of liquid and vapour phase can be reconstructed from :math:`\phi_l` and :math:`\phi_v`, respectively.

.. warning:: 

  How to set value for :math:`\mu_l` in vapour region and :math:`\mu_v` in liquid region ? 
  They are set to :code:`inf` at the moment, and variable, e.g. :code:`rAU_l` (:math:`k\frac{k_{rl}}{\mu_l}`) will be zero in vapour region. Therefore a tiney value should be add in the denominator in line 53-54 of :numref:`lst:pEqn:multiphase`.
  **Is there any better solution?**

.. code-block:: cpp
  :linenos:
  :emphasize-lines: 41, 47, 48, 50, 51, 53, 54
  :name: lst:pEqn:multiphase
  :caption: Implementation of pressure equation of multiphase model

  volScalarField rAU_l(permeability*permeability_l/mu_l); //K/mu
  volScalarField rAU_v(permeability*permeability_v/mu_v); //K/mu
  volScalarField M_l(rho_l*rAU_l);
  volScalarField M_v(rho_v*rAU_v);
  volScalarField L_l(rho_l*M_l);
  volScalarField L_v(rho_v*M_v);  
  
  surfaceScalarField rhorAUf_l("rhorAUf_l", fvc::interpolate(M_l));
  surfaceScalarField rhorAUf_v("rhorAUf_v", fvc::interpolate(M_v));
  surfaceScalarField M_lf("M_lf", fvc::interpolate(M_l));//M_l on surface
  surfaceScalarField M_vf("M_vf", fvc::interpolate(M_v));//M_v on surface
  surfaceScalarField L_lf("L_lf", fvc::interpolate(L_l));//L_l on surface
  surfaceScalarField L_vf("L_vf", fvc::interpolate(L_v));//L_v on surface

  volVectorField HbyA(U*0);
  volScalarField rAU(permeability/mu); //K/mu
  surfaceScalarField rhorAUf("rhorAUf", fvc::interpolate(rho*rAU));//rho/A on surface
  surfaceScalarField phig("phig",(fvc::interpolate(rho)*rhorAUf * g) & mesh.Sf());
  // surfaceScalarField phig("phig",((fvc::interpolate(rho_l)*rhorAUf_l +fvc::interpolate(rho_v)*rhorAUf_v ) * g) & mesh.Sf());
  
  surfaceScalarField phiHbyA
  (
      "phiHbyA",
      phig
  );
  // Update the pressure BCs to ensure flux consistency
  // constrainPressure(p, rho, U, phiHbyA, rhorAUf);

  fvScalarMatrix p_rghDDtEqn
  (
      porosity*rho*betaT*fvm::ddt(p)
      -porosity*rho*alphaP*fvc::ddt(T)
      +fvc::div(phiHbyA)
  );
  while (pimple.correctNonOrthogonal())
  {
      fvScalarMatrix pEqn
      (
          p_rghDDtEqn 
          // - fvm::laplacian(rhorAUf, p)
            - fvm::laplacian(rhorAUf_l, p) - fvm::laplacian(rhorAUf_v, p)
      );
      pEqn.solve();
      if (pimple.finalNonOrthogonalIter())
      {
          // option 2: using flux reconstruct velocity, magic function of reconstruct
          surfaceScalarField phip("phip",pEqn.flux());
          phi = phiHbyA + phip;
          
          surfaceScalarField phi_l("phi_l", phip*M_lf/(M_lf+M_vf) + phig*L_lf/(L_lf + L_vf));
          surfaceScalarField phi_v("phi_v",phi-phi_l);
          // to avoid rhorAUf_l or rhorAUf_v equal to zero, need to plus a tiney value 
          U_l = HbyA + rAU_l*fvc::reconstruct(phi_l/(rhorAUf_l + dimensionedScalar("tiney",dimensionSet(rhorAUf_l.dimensions()),1e-25)));
          U_v = HbyA + rAU_v*fvc::reconstruct(phi_v/(rhorAUf_v + dimensionedScalar("tiney",dimensionSet(rhorAUf_l.dimensions()),1e-25)));
          U_l.correctBoundaryConditions();
          U_v.correctBoundaryConditions();
          U = HbyA + rAU*fvc::reconstruct((phig + pEqn.flux())/rhorAUf);
          U.correctBoundaryConditions();
      }
  }

Energy equation
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: cpp
  :linenos:
  :emphasize-lines: 1
  :name: lst:EEqn:multiphase
  :caption: Implementation of energy equation of multiphase model

  // rock-diffusive part
  fvScalarMatrix TEqn_rock
  (
    ((1.0-porosity)*rho_rock*cp_rock)*fvm::ddt(T)
    == 
    fvm::laplacian(kr,T)
  );
  TEqn_rock.solve();

  // fluid-advective energy by enthalpy
  fvScalarMatrix hEqn_liquid
  (
      (rho)*fvm::ddt(h)
      == 
      - fvc::div(phi_l,h_l)
      - fvc::div(phi_v,h_v)
      // add aditional terms later
  );
  hEqn_liquid.solve();

.. note::

  In fluid advection part, we adopt explicit scheme for liquid and vapour advection, but implicit scheme for transient term.

When :code:`TEqn_rock, hEqn_liquid` are solved, 
we can get energy(:math:`H_r = \rho_rC_{pr}T`) of rock and energy(:math:`H_f = \rho_l h_l + \rho_v h_v`) in fluid,
then we need a function to calculate thermal equilibrium(**energy redistribution between rock and fluid to make sure the temperature is equal ?**) to get a new temperature :code:`T`.
For a specific node, we could design a function as below,

.. code-block:: cpp

  double ThermalEquilibrium(double p, double h, double T0, const double rho_r, const double cp_r, const double porosity)
  {
    double H_r=rho_r*cp_r*T; //energy in rock [J/m^3] or [J] ?
    double H_f=.....;       //energy in fluid
    double H_t=H_r + H_f;  //total energy
    Steamstate S = freesteam_set_ph(p,h); //get fluid state
    int region = freesteam_region(S);
    double Ttest = freesteam_T(S); 
    double Tnew = T0;
    ....
    ....
    return Tnew;
  }

.. list-table:: Definitions and values of variables used in the :ref:`model_multiphase_darcy`.
   :header-rows: 1
   :name: tab:symbols:multiphase

   * - Symbol 
     - Definition
     - Value
     - Unite
     - Variable name: OpenFOAM class
   * - :math:`\vec{g}`
     - Gravitational acceleration vector
     - 9.81
     - :math:`m\ s^{-2}`
     - :code:`g: uniformDimensionedVectorField`
   * - :math:`T`
     - Temperature
     -  
     - :math:`K`
     - :code:`T: volScalarField`
   * - :math:`i`
     - Fluid phase index (:math:`i=l, v, s`)
     -  
     - 
     - 
   * - :math:`h_i`
     - Specific enthalpy 
     -  
     - :math:`J\ kg^{-1}`
     - :code:`enthalpy_i: volScalarField`
   * - :math:`p`
     - Pressure
     -  
     - :math:`Pa`
     - :code:`p: volScalarField`
   * - :math:`k`
     - Permeability
     -  
     - :math:`m^2`
     - :code:`permeability: volScalarField`
   * - :math:`k_{ri}`
     - Relative permeability 
     -  
     - 
     - :code:`r_permeability_i: volScalarField`
   * - :math:`S_i`
     - Saturation 
     -  
     - 
     - :code:`saturation_i: volScalarField`
   * - :math:`\vec{U_i}`
     - Darcy velocity 
     -  
     - :math:`m\ s^{-1}`
     - :code:`U_i: volVectorField`
   * - :math:`\Delta T`
     - Time step
     -  
     - :math:`s`
     - :code:`deltaT_: scalar`
   * - :math:`C_o`
     - Courant number
     -   
     - 
     - :code:`CoNum: scalar`
   * - :math:`C_{\Delta t}`
     - Coefficient for time-step change
     -   
     -  
     - :code:`maxDeltaTFact: scalar`
   * - :math:`\vec{q_h}`
     - Heat flux 
     -   
     -  :math:`W\ m^{-2}`
     -  :code:`q_: scalarField`
   * - :math:`\vec{\phi_g}`
     - Gravity related flux
     -   
     - :math:`kg\ s^{-1}`
     - :code:`phig: surfaceScalarField`
   * - :math:`\vec{\phi_m}`
     - Mass flux 
     -  
     - :math:`kg\ m^{-2}\ s^{-1}`
     - :code:`phi: surfaceScalarField`
   * - :math:`\vec{n}`
     - Normal vector of face 
     -   
     - 
     - 
   * - :math:`\mu_i` 
     - Dynamic viscosity  
     -  
     - :math:`Pa\ s`
     - :code:`mu_i: volScalarField`
   * - :math:`\rho_i` 
     - Density 
     - 
     - :math:`kg\ m^{-3}`
     - :code:`rho_i: volScalarField`
   * - :math:`\rho_f` 
     - Density of fluid (:math:`\rho_f = \sum{S_i\rho_i}, i=l, v, s`)
     - 
     - :math:`kg\ m^{-3}`
     - :code:`rho: volScalarField`
   * - :math:`\alpha_i`
     - Thermal expansivity 
     - 
     - :math:`K^{-1}`
     - :code:`alphaP_i: volScalarField`
   * - :math:`\beta_i`
     - Compressibility 
     -  
     - :math:`Pa^{-1}`
     - :code:`betaT_i: volScalarField`
   * - :math:`\varepsilon`
     - Porosity of rock
     - 0.1
     -  
     - :code:`porosity: dimensionedScalar`
   * - :math:`\rho_r`
     - Density of rock
     - 2750
     - :math:`kg\ m^{-3}`
     - :code:`rho_rock: dimensionedScalar`
   * - :math:`C_{pr}`
     - Specific heat of rock
     - 880
     - :math:`J\ kg^{-1}\ K^{-1}`
     - :code:`cp_rock: dimensionedScalar`
   * - :math:`\lambda_{r}`
     - Thermal conductivity of rock
     - 1.5
     - :math:`W\ m^{-1}\ K^{-1}`
     - :code:`kr: dimensionedScalar`
   * - :math:`Q_{H_2O}`
     - Source term
     - 
     - 
     - :code:`Q_mass: dimensionedScalar`

.. todo::

    完善多相流模型的参数表格