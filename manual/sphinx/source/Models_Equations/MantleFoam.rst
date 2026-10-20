.. _MantleConvectionFoam:

.. include:: /include.rst_

.. _model_MantleConvection:

============================================================================
Mantle convection
============================================================================

Introduction
==============

**MantleConvectionFoam** is the simple version of ASPECT_, it will be used to develop hydro-thermo-mechanical model.

Theory
=========

The motion of a highly viscous fluid driven by differences in the gravitational force due to a density that depends on the temperature.

Basic equations
=====================

* Momentum conservation

.. math::
    :label: eq:MantleConvectionFoam:momentum 

    \nabla \cdot \color{red}{\tau} - \nabla p + \rho \vec{g} = 0

* Mass conservation 

.. math::
  :label: eq:MantleConvectionFoam:conti 

  \nabla \cdot (\rho \vec{U}) = 0

* Energy conservation 

.. math::
  :label: eq:MantleConvectionFoam:energy

  \rho C_p \left( \frac{\partial T}{\partial t} + \vec{U}\cdot \nabla T \right) - \nabla \cdot \lambda \nabla T = \rho H + 2\mu (\color{red}{\tau} : \color{red}{\tau}) + \alpha T(\vec{U}\cdot \nabla p) + \rho T \Delta S \left( \frac{\partial X}{\partial t} + \vec{U}\cdot \nabla X \right)

where :math:`\tau` is the **shear rate tensor** (or viscous stress tensor), :math:`\mathbf{D}` is the **strain rate tensor**.

.. math::
  :label: eq:MantleConvectionFoam:shearRateTensor

  \color{red}{\tau} = \underbrace{2\mu \mathbf{D} - \frac{2}{3} \mu (\nabla \cdot \vec{U})\mathbf{I}}_{\text{viscous stress tensor}}

.. math::
  :label: eq:strainRate:D

  \mathbf{D} = \underbrace{\frac{1}{2} \left[ \nabla \otimes \vec{U} + (\nabla \otimes \vec{U})^{T} \right]}_{\text{strain rate tensor}}


Implementations
===================

Divergence of viscous stress tensor 
--------------------------------------------

.. tab:: Equation to code 

  * :math:`\nabla \cdot \tau` -> :code:`-fvm::laplacian(mu,U) -fvc::div(mu*dev2(T(fvc::grad(U))))`

.. tab:: Equation derivation and proof

  .. include:: proof_MantleFoam_divTau.rst_

Pressure equation
--------------------------------------------

.. tab:: Code of pEqn.H

  * **UEqn.H**
  
  .. code-block:: cpp

    fvVectorMatrix UEqn
    (
        -fvm::laplacian(mu,U)
        -fvc::div(mu*dev2(T(fvc::grad(U))))
    );

  .. * **pEqn.H**

  .. .. code-block:: cpp 

  ..   volScalarField rAU("rAU", 1.0/UEqn.A()); 
  ..   surfaceScalarField rAUf("rAUf", fvc::interpolate(rAU)); 
  ..   volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));
  ..   surfaceScalarField phiHbyA("phiHbyA", fvc::flux(HbyA) );
  ..   surfaceScalarField phiG ( rAUf*fvc::interpolate(rho)*(g & mesh.Sf()) );
  ..   phiHbyA += phiG;
  ..   constrainPressure(p, U, phiHbyA, rAUf);
  ..   fvScalarMatrix pEqn( fvm::laplacian(rAUf, p) == fvc::div(phiHbyA));
  ..   pEqn.solve();
  ..   phi = phiHbyA - pEqn.flux();
  ..   U = HbyA + rAU*fvc::reconstruct((phiG - pEqn.flux())/rAUf);

After discretizing the momentum equation and get :code:`UEqn` matirx, then it's pretty easy to construct pressure equation and solve it.

.. tab:: Semi-discretization of momentum equation

  .. include:: proof_MantleFoam_pEqn.rst_

Rhelogy 
==============

Viscous rheology 
----------------------

.. tab:: Equations 

  See also :cite:`gerya2010introduction` (page 73-75).

  .. math::
    :label: eq:mu:Dislocation

    \mu =  \frac{1}{2}A_D^{-\frac{1}{n}}\color{red}{d^{\frac{m}{n}}}(\dot{\varepsilon}_{\text{II}})^{\frac{1-n}{n}} \text{exp}\left( \frac{E_a+PV_a}{nRT} \right)

  .. list-table:: Definitions and values of variables used in viscous rheology.
    :header-rows: 1
    :name: tab:symbols:MantleFoam:rheology

    * - Symbol 
      - Physical meaning
      - Typical value
      - Unit
    * - :math:`P`
      - Pressure
      - 
      - :math:`Pa`
    * - :math:`T`
      - Temperature
      - 
      - :math:`K`
    * - :math:`\mu`
      - Viscosity
      - :math:`10^{21}`
      - :math:`Pa s`
    * - :math:`R`
      - Gas constant
      - :math:`8.3145`
      - :math:`JK^{-1}mol^{-1}`
    * - :math:`d`
      - Grain size
      - 
      - :math:`m`
    * - :math:`A_D`
      - Material constant
      - :math:`3.6\times 10^{-14}`
      - :math:`Pa^{-n}s^{-1}m^{-m}`
    * - :math:`n`
      - Stress exponent 
      - :math:`n=1` for diffusion creep, :math:`n>1` (e.g. :math:`3.5`) for dislocation creep
      - 
    * - :math:`m`
      - Grain size exponent
      - :math:`m<0` for diffusion creep, :math:`m=0` for dislocation creep 
      - 
    * - :math:`E_a`
      - Activation energy 
      - :math:`520\times 10^3`
      - :math:`J mol^{-1}`
    * - :math:`V_a`
      - Activation volume 
      - :math:`22\times 10^{-6}`
      - :math:`J Pa^{-1}`
    * - :math:`\dot{\varepsilon}_{\text{II}}`
      - Second invariant of the deviatoric strain rate tensor
      - 
      - :math:`J Pa^{-1}`
    
  .. math:: 
    
    \begin{align}
      \dot{\varepsilon}_{\text{II}} = & \sqrt{\color{red}{J_2}\left[ \text{dev}( \varepsilon (\vec{U}) \right]}, \color{red}{J_2} \text{ operator means the second invariant of the tensor} \\
      \varepsilon (\vec{U}) = & \frac{1}{2} \left( \nabla \otimes \vec{U} + (\nabla \otimes \vec{U})^T \right) \\
      \text{dev}\left[ \varepsilon (\vec{U}) \right] = & \frac{1}{2} \left( \nabla \otimes \vec{U} + (\nabla \otimes \vec{U})^T \right) - \frac{1}{3} (\nabla \cdot \vec{U})\mathbf{I}
    \end{align}

  .. admonition:: Second invariant of a symmetric tensor :math:`\mathbf{A}`

    :math:`\color{red}{J_2} (\mathbf{A}) = \frac{1}{2} \left(tr(\mathbf{A})^2 - tr(\mathbf{A^2}) \right)`

    It's easy to proof that, :math:`\color{red}{J_2} (\mathbf{A}) = A_{00}A_{11} + A_{00}A_{22} + A_{11}A_{22} - A_{01}^2 - A_{02}^2 - A_{12}^2`.

.. tab:: ASPECT Implementations

  * :math:`\dot{\varepsilon}_{\text{II}}`: square root of the second invariant for the deviatoric strain rate

  .. code-block:: cpp
    :caption: source/material_model/rheology/visco_plastic.cc

    // Calculate the square root of the second moment invariant for the deviatoric strain rate tensor.
    edot_ii = std::max(std::sqrt(std::fabs(second_invariant(deviator(in.strain_rate[i])))),
                             min_strain_rate);

  The can be found in Deal.II library: `second_invariant(.cc) <https://www.dealii.org/developer/doxygen/deal.II/symmetric__tensor_8h_source.html#l02748>`_ and `second_invariant(.h) <https://www.dealii.org/developer/doxygen/deal.II/classSymmetricTensor.html#ae1a406452573ef4f85351abd4a4bc4c0>`_.

  * :math:`\mu`

  .. code-block:: cpp 
    :caption: source/material_model/rheology/visco_plastic.cc

    // Step 1b: compute viscosity from dislocation creep law
    const double viscosity_dislocation = dislocation_creep.compute_viscosity(edot_ii, in.pressure[i], temperature_for_viscosity, j,
                                                                                     phase_function_values,
                                                                                     n_phases_per_composition);
  

  .. code-block:: cpp 
      :caption: source/material_model/rheology/dislocation_creep.cc
      
      // Power law creep equation:
      //    viscosity = 0.5 * A^(-1/n) * edot_ii^((1-n)/n) * exp((E + P*V)/(nRT))
      // A: prefactor, edot_ii: square root of second invariant of deviatoric strain rate tensor,
      // E: activation energy, P: pressure,
      // V; activation volume, n: stress exponent, R: gas constant, T: temperature.
      double viscosity_dislocation = 0.5 * std::pow(p.prefactor,-1/p.stress_exponent) *
                                      std::exp((p.activation_energy + pressure*p.activation_volume)/
                                              (constants::gas_constant*temperature*p.stress_exponent)) *
                                      std::pow(strain_rate,((1. - p.stress_exponent)/p.stress_exponent));

.. todo::

  * 当顶部使用速度边界条件的时候，出现压力负值，如果使用了viscos rheology模型，则会使这种问题越来越严重，直至奔溃。因此必须解决压力负值的问题！！！可使用常数viscosity来测试直至压力正常
  * 求解器的动量方程已经按照ASPECT manual的公式（1）完成了,接下来搞清楚各种rheology模型！

