.. _SinglePhaseDBSFoam:

.. include:: /include.rst_

.. _model_SinglePhaseDBSFoam:

============================================================================
Single phase DBS flow model
============================================================================

Introduction
==============

SinglePhaseDBSFoam solver is designed to solve flow solution in a hybrid-scale porous medium, especially hydrothermal flow in oceanic crust, 
based on micro-continuum approach proposed by :cite:`soulaine2016micro` which relying on the DBS(Darcy-Brinkman-Stokes) equation :cite:`brinkman1949calculation`.
The momentum conservation can be described by a single DBS equation for both porous region and solid-free region. 
The solver development is based on several exist solvers, 
 
1) dbsFoam_ : single phase incompressible hybrid-scale solver without gravity term :cite:`soulaine2016micro`.

2) hybridPorousInterFoam_ : incompressible, immiscible two-phase Newtonian fluid flow in hybrid porous medium :cite:`carrillo2020multiphase`.

3) htSinglePhaseDarcyFoam_: single phase buoyant driven compressible Darcy flow in porous medium :cite:`guo2020hydrothermalfoam`.

4) impesFoam_: multi-phase macro-scale Darcy flow :cite:`horgue2015open`. 

5) buoyantPimpleFoam_: transient solver for buoyant, turbulent flow of compressible fluids for ventilation and heat-transfer.

Governing equations
========================

Continuity equation 
------------------------

.. math::
  :label: eq:SinglePhaseDBSFoam:conti

    \varepsilon \frac{\partial \rho}{\partial t} + \nabla \cdot \left( \rho \vec{U} \right) = 0

Momentum equation
----------------------

.. math:: 
  :label: eq:SinglePhaseDBSFoam:momentum

  \underbrace{\frac{1}{\varepsilon} \left( \frac{\partial \rho \vec{U}}{\partial t} + \nabla \cdot(\frac{\rho}{\varepsilon} \vec{U}\vec{U}) \right)}_{\text{Inertial}} = \underbrace{\frac{1}{\varepsilon}\nabla \cdot \tau}_{\text{Viscous}} - \underbrace{\frac{\mu}{k}\vec{U}}_{\text{D-B Drag}} -\nabla p + \rho \vec{g} , \left\{\begin{matrix}
  \varepsilon =1 ,\text{solid-free region}, \frac{\mu}{k}=0\\
  \varepsilon \in (0,1) , \text{porous region}
  \end{matrix} \right.

where :math:`\varepsilon` is the macro-scale porosity.
:math:`k` is the permeability, :math:`\mu` is the dynamic viscosity of the fluid. 
:math:`\tau(\vec{U}) = \mu \left(\nabla \vec{U} + (\nabla \vec{U})^T \right) - \frac{2}{3}\mu(\nabla \cdot \vec{U})\mathbf{I}` is the viscous stress tensor (see equation 1.2-7 and section 1.2 of :cite:`bird2006transport`), which could be simplified for a specific problem. **For hydrothermal flow, the second term will be ignored in the following sections**.

.. tab:: Compressible

  * Momentum equation 

  .. math::

    \underbrace{\frac{1}{\varepsilon} \left( \frac{\partial \rho \vec{U}}{\partial t} + \nabla \cdot(\frac{\rho}{\varepsilon} \vec{U}\vec{U}) \right)}_{\text{Inertial}} = \underbrace{\frac{1}{\varepsilon}\nabla \cdot \left( \mu \left(\nabla \vec{U} + (\nabla \vec{U})^T \right) - \frac{2}{3}\mu(\nabla \cdot \vec{U})\mathbf{I} \right)}_{\text{Viscous}} - \underbrace{\frac{\mu}{k}\vec{U}}_{\text{D-B Drag}} -\nabla p + \rho \vec{g}


.. tab:: Incompressible 

  * Continuity equation 

  .. math::

    \nabla \cdot \vec{U} = 0

  * Momentum equation 

  For incompressible fluid, it can be proved that :math:`\nabla \cdot (\nabla \vec{U})^T =0`, so the momentum equation reduces to 

  .. math::

    \underbrace{\frac{1}{\varepsilon} \left( \frac{\partial \vec{U}}{\partial t} + \frac{1}{\varepsilon} \nabla  \cdot( \vec{U}\vec{U}) \right)}_{\text{Inertial}} = \underbrace{\frac{1}{\varepsilon} \nabla \cdot \nu \nabla \vec{U}}_{\text{Viscous}} - \underbrace{\frac{\nu}{k}\vec{U}}_{\text{D-B Drag}} -\nabla \frac{p}{\rho} + \vec{g}
  
  where :math:`\nu = \mu/\rho` is the kinematic viscosity.
 
   .. admonition:: prove :math:`\nabla \cdot (\nabla \vec{U})^T = 0` when :math:`\nabla \cdot \vec{U} = 0`

    .. math::
      
      \nabla \vec{U} = \left[ \begin{matrix}
      \frac{\partial }{\partial x} \\
      \frac{\partial }{\partial y} \\
      \frac{\partial }{\partial z}
      \end{matrix} \right] \left[ U_x ~  U_y ~ U_z \right]
      = \left[ \begin{matrix}
      \frac{\partial U_x}{\partial x} & \frac{\partial U_y}{\partial x} & \frac{\partial U_z}{\partial x} \\
      \frac{\partial U_x}{\partial y} & \frac{\partial U_y}{\partial y} & \frac{\partial U_z}{\partial y} \\
      \frac{\partial U_x}{\partial z} & \frac{\partial U_y}{\partial z} & \frac{\partial U_z}{\partial z}
      \end{matrix} \right]

      \Rightarrow {\color{red}{\nabla}} \cdot (\nabla \vec{U})^T = {\color{red}{\nabla}} \cdot \left[ \begin{matrix}
      \frac{\partial U_x}{\partial x} & \frac{\partial U_x}{\partial y} & \frac{\partial U_x}{\partial z} \\
      \frac{\partial U_y}{\partial x} & \frac{\partial U_y}{\partial y} & \frac{\partial U_y}{\partial z} \\
      \frac{\partial U_z}{\partial x} & \frac{\partial U_z}{\partial y} & \frac{\partial U_z}{\partial z}
      \end{matrix} \right] = \left[ \begin{matrix}
      {\color{red}{\frac{\partial }{\partial x}}}(\frac{\partial U_x}{\partial x}) + {\color{red}{\frac{\partial }{\partial y}}}(\frac{\partial U_y}{\partial x}) + {\color{red}{\frac{\partial }{\partial z}}} (\frac{\partial U_z}{\partial x}) \\
      {\color{red}{\frac{\partial }{\partial x}}}(\frac{\partial U_x}{\partial y}) + {\color{red}{\frac{\partial }{\partial y}}}(\frac{\partial U_y}{\partial y}) + {\color{red}{\frac{\partial }{\partial z}}} (\frac{\partial U_z}{\partial y}) \\
      {\color{red}{\frac{\partial }{\partial x}}}(\frac{\partial U_x}{\partial z}) + {\color{red}{\frac{\partial }{\partial y}}}(\frac{\partial U_y}{\partial z}) + {\color{red}{\frac{\partial }{\partial z}}} (\frac{\partial U_z}{\partial z}) \\
      \end{matrix} \right] = \left[ \begin{matrix} 
      \frac{\partial ({\color{red}{\nabla}} \cdot \vec{U})}{\partial x}  \\
      \frac{\partial ({\color{red}{\nabla}} \cdot \vec{U})}{\partial y}  \\
      \frac{\partial ({\color{red}{\nabla}} \cdot \vec{U})}{\partial z} 
      \end{matrix} \right]  =0


Energy conservation 
-------------------------

.. tab:: Hybrid-scale 

  .. math::
    :label: eq:SinglePhaseDBSFoam:energy

    \left(\varepsilon \rho C_{pf} + (1-\varepsilon)\rho_r C_{pr} \right) \frac{\partial T}{\partial t} = \nabla \cdot (\lambda_r \nabla T) - \rho C_{pf} \vec{U}\cdot \nabla T + \frac{\mu_f}{k} \parallel \vec{U} \parallel ^2 - \left( \frac{\partial ln \rho}{\partial ln T} \right)_p \frac{Dp}{Dt}

.. tab:: General form

  :cite:`bird2006transport` (p. 337, eq. 112-5) gives the general form of energy conservation equation in terms of temperature,

  .. math:: 

    \rho C_p \frac{DT}{Dt} = -\nabla \cdot \lambda \nabla T - (\tau : \nabla \vec{U}) - \left( \frac{\partial ln \rho }{\partial ln T} \right)_p \frac{Dp}{Dt}

.. todo::

  The energy equation for the hybrid-scale porous flow need to be confirmed again! The thermal conductivity :math:`\lambda_r` should be thermal conductivity of water in solid-free region ? How to express the thermal diffusion term in a proper form ?

.. admonition:: Material derivative

  For a field variable :math:`\phi (t,\vec{X}(t))` which could be a scalar field or vector field, its material derivative is given by :eq:`eq:DDt` (see also eq. 3.2 of :cite:`moukalled2016finite`.), 

  .. math::
    :label: eq:DDt

    \frac{D\phi}{Dt} = \frac{\partial \phi}{\partial t} + \frac{\partial \phi}{\partial x}\underbrace{\frac{\partial x}{\partial t}}_{u} + \frac{\partial \phi}{\partial y}\underbrace{\frac{\partial y}{\partial t}}_{v}+ \frac{\partial \phi}{\partial z}\underbrace{\frac{\partial z}{\partial t}}_{w} = \frac{\partial \phi}{\partial t} + (\vec{U}\cdot \nabla) \phi

.. figure:: images/SinglePhaseDBSFoam/thermalConductivity_water.*
    :align: center
    :width: 500 px
    :name: fig:SinglePhaseDBSFoam:thermalConductivity_water

    Thermal conductivity of water as a function of temperature and pressure.


OpenFOAM implementations 
==============================

Let's derive the above equations into "OpenFOAM's format". 
The first step is constructing the Poisson equation of pressure by combing the momentum equation :eq:`eq:SinglePhaseDBSFoam:momentum` and continuity equation :eq:`eq:SinglePhaseDBSFoam:conti`.

1. Implicit discrete of Transient term of equation :eq:`eq:SinglePhaseDBSFoam:momentum` using a Euler implicit difference scheme (see also Eq. 47 in :cite:`carrillo2020multiphase`):

.. math::

  \int\int\int \frac{\partial \rho \vec{U}}{\partial t} dV dt =  \left (\rho ^{n+1} {\color{red}{\vec{U}^{n+1}}} - \rho ^{n} \vec{U}^{n} \right ) V

.. todo::

  How to process/explain the :math:`\rho^{n+1}` ? hybridPorousInterFoam_ implement this term as :code:`fvm::ddt(rho, U)`. But how does it works in OpenFOAM? is there any assumption is taken here ? because :math:`\rho^{n+1}` should be a unknown as well.

2. Advection term of :eq:`eq:SinglePhaseDBSFoam:momentum` (linearization of the nonlinear term),

.. math::

  \begin{matrix}
  \int\int\int \nabla \cdot \left( \frac{\rho}{\varepsilon} \vec{U}\otimes \vec{U} \right) dV dt = \Delta t\int\int \frac{\rho}{\varepsilon}\vec{U}\vec{U} \cdot d\vec{S} =\Delta t \sum\limits_{f(V)} \left( \vec{U}^{n+1}\frac{\rho \vec{U}^n}{\varepsilon} \right)_f \cdot \vec{S}_f  \\
  = {\color{blue}{\Delta t \sum\limits_{f(V)} \frac{\phi}{\varepsilon}}} {\color{red}{\vec{U}^{n+1}_f}}
  \end{matrix}

.. tip::

  Using cell centered value construct face value, so the discrete coefficience depends on interpolate scheme. 

3. Laplacian term (viscous term) of :eq:`eq:SinglePhaseDBSFoam:momentum`,

.. math::

  \int\int\int \left(\nabla \cdot \tau(\vec{U}^{n+1}) \right) dVdt = \Delta t\int\int \tau_f \cdot d\vec{S}  = {\color{blue}{\Delta t \sum\limits_{f(V)} \tau(}}{\color{red}{\vec{U}^{n+1}}}{\color{blue}{)_f \cdot \vec{S}_f}}

.. tip::

  Using cell centered values (include neighbor cells) to construct gradient on faces. :math:`\tau(\vec{U}) = \mu \left(\nabla \vec{U} + (\nabla \vec{U})^T \right) - \frac{2}{3}\mu(\nabla \cdot \vec{U})\mathbf{I}`
  ==> :math:`\mu\left( \nabla \vec{U} +  {\color{red}{(\nabla \vec{U})^T - \frac{2}{3} tr((\nabla \vec{U})^T)\mathbf{I}}}\right)`
  ==> :math:`\mu\left( \nabla \vec{U} +  {\color{red}{dev2((\nabla \vec{U})^T)}}\right)`. It is implemented in OpenFOAM as :code:`fvm::laplacian(mu, U) + fvc::div(mu*dev2(T(fvc::grad(U))))`.

4. D-B drag term and gravity as a source term. 


Therefore, :eq:`eq:SinglePhaseDBSFoam:momentum` can be expressed in a semi-discrete form, 

.. math::

  V\left( \frac{\rho^{n+1} \vec{U}^{n+1}_P - \rho^n\vec{U}^n_P}{\Delta t} \right) = -a_P^{\prime} \vec{U}^{n+1} + \sum\limits_{NP} (a_{NP}^{\prime} \vec{U}^{n+1}_{NP}) - K_{fs} \vec{U}^{n+1} - \nabla p + \rho \vec{g}

where :math:`V` and :math:`\Delta t` represent cell volume and time step. 
The subscript :math:`P` denotes values at the cell center. 
:math:`a_P^{\prime}` and :math:`a_{NP}^{\prime}` represent discrete coefficients related to the advection term and laplacian term. 

Rearrange the above semi-discrete form,

.. math::

  \left( \frac{V\rho^{n+1}}{\Delta t} + a_P^{\prime} + K_{fc} \right)\vec{U}^{n+1}_P = \sum\limits_{NP} (a_{NP}^{\prime} \vec{U}^{n+1}_{NP}) + \vec{S} -\nabla p + \rho \vec{g} 

where :math:`\vec{S} = \frac{V\rho^n \vec{U}_P^n}{\Delta t}` is the explicit source term. 

This equation forms a matrix system that results the momentum equation discretization. 
Following the OpenFOAM notations, we define :math:`A_P = \frac{V\rho^{n+1}}{\Delta t} + a_P^{\prime} + K_{fc}` and :math:`\mathbf{H} = \sum\limits_{NP} (a_{NP}^{\prime} \vec{U}^{n+1}_{NP}) + \vec{S}`, therefore the discretization form of the momentum equation can be written as,

.. math::

  A_P \vec{U}_P^{n+1} = \mathbf{H} - \nabla p + \rho \vec{g}

.. tip::

  The terms except :math:`-\nabla p + \rho \vec{g}` of the momentum equation, :math:`\underbrace{\frac{1}{\varepsilon} \left( \frac{\partial \rho \vec{U}}{\partial t} + \nabla \cdot(\frac{\rho}{\varepsilon} \vec{U}\vec{U}) \right)}_{\text{Inertial}} = \underbrace{\frac{1}{\varepsilon}\nabla \cdot \left( \mu \left(\nabla \vec{U} + (\nabla \vec{U})^T \right) - \frac{2}{3}\mu(\nabla \cdot \vec{U})\mathbf{I} \right)}_{\text{Viscous}} - \underbrace{\frac{\mu}{k}\vec{U}}_{\text{D-B Drag}}`, are usually be discretized in :code:`UEqn.H` to construct the coefficient matrix :code:`UEqn`. This fvMatrix_ object has member function named :code:`A()` and :code:`H()` which can obtain the coefficient :math:`A_P` and :math:`\mathbf{H}`. 

.. math::

  \vec{U}_P^{n+1} = \frac{\mathbf{H}}{A_P} - \frac{1}{A_P} \left( \nabla p - \rho \vec{g} \right)

Substitute the above equation into :eq:`eq:SinglePhaseDBSFoam:conti`, we can get

.. math::

  \varepsilon \frac{\partial \rho}{\partial t} + \nabla \cdot \left(\mathbf{rhoHbyA} + \frac{\rho}{A_P}\rho \vec{g} \right) = \nabla \cdot \frac{\rho}{A_P}\nabla p 

where :math:`\mathbf{rhoHbyA} = \frac{\rho\mathbf{H}}{A_P}`, density is a function of temperature and pressure, which can be expressed as :math:`\frac{\partial \rho}{\partial t} = \rho \left(\beta \frac{\partial p}{\partial t} - \alpha \frac{\partial T}{\partial t} \right)` with :math:`\beta` is the compressibility and :math:`\alpha` is the thermal expansivity of the fluid, which can be calculated from the EOS (see :cite:`guo2020hydrothermalfoam`). Therefore the pressure equation can be written as,

.. math::

  \varepsilon \rho \beta \frac{\partial p}{\partial t} - \varepsilon \rho \alpha \frac{\partial T}{\partial t} + \nabla \cdot \left(\mathbf{HbyA} + \frac{1}{A_P}\rho \vec{g} \right) = \nabla \cdot \frac{\rho}{A_P}\nabla p 
