.. _HydrothermalSinglePhaseDarcyFoam:

.. include:: /include.rst_

.. _model_singlephase_darcy:

======================================
Single-phase Darcy flow model
======================================


Governing equations
=======================

The solver is named :code:`HydrothermalSinglePhaseDarcyFoam`, 
which is designed to resolve fluid flow within submarine hydrothermal circulation systems.
The hydrothermal fluid flow is governed by Darcy's law (Eqn. :eq:`eq:darcy`), 
mass continuity (Eqn. :eq:`eq:conti`) and energy conservation (Eqn. :eq:`eq:temperature`) equations shown below, 

.. math::
    :label: eq:darcy 

    \vec{U} = - \frac{k}{\mu_f} (\nabla p -\rho \vec{g})
    
.. math::
    :label: eq:conti
    
    \varepsilon \frac{\partial \rho_f}{\partial t} + \nabla \cdot (\vec{U} \rho_f) = 0

.. math::
    :label: eq:pressure
    
    \varepsilon \rho_f \left( \beta_f \frac{\partial p}{\partial t} - \alpha_f \frac{\partial T}{\partial t} \right) = \nabla \cdot \left( \rho_f \frac{k}{\mu_f} (\nabla p - \rho_f \vec{g}) \right)

.. math::
    :label: eq:temperature
    
    (\varepsilon \rho_f C_{pf} + (1-\varepsilon)\rho_r C_{pr})\frac{\partial T}{\partial t} = \nabla \cdot (\lambda_r \nabla T) - \rho_f C_{pf} \vec{U}\cdot \nabla T + \frac{\mu_f}{k} \parallel \vec{U} \parallel ^2 - \left( \frac{\partial ln \rho_f}{\partial ln T} \right)_p \frac{Dp}{Dt}

where the pressure equation :eq:`eq:pressure` is derived from continuity equation :eq:`eq:conti` and Darcy's law :eq:`eq:darcy` (see :cite:`hasenclever2014hybrid`). All symbols are defined in :numref:`tab:symbols` .

.. list-table:: Definitions and values of variables used in the :ref:`model_singlephase_darcy`
   :header-rows: 1
   :name: tab:symbols

   * - Symbol 
     - Definition
     - Value
     - Unit
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
   * - :math:`\vec{U}`
     - Darcy velocity
     -  
     - :math:`m\ s^{-1}`
     - :code:`U: volVectorField`
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
   * - :math:`C_{pf}` 
     - Specific heat of fluid
     -  
     - :math:`m^2\ s^{−2}\ K^{−1}`
     - :code:`Cp: volScalarField`
   * - :math:`\mu_f` 
     - Dynamic viscosity of fluid 
     -  
     - :math:`Pa\ s`
     - :code:`mu: volScalarField`
   * - :math:`\rho_f` 
     - Density of fluid
     - 
     - :math:`kg\ m^{-3}`
     - :code:`rho: volScalarField`
   * - :math:`\alpha_f`
     - Thermal expansivity
     - 
     - :math:`K^{-1}`
     - :code:`alphaP: volScalarField`
   * - :math:`\beta_f`
     - Compressibility
     -  
     - :math:`Pa^{-1}`
     - :code:`betaT: volScalarField`
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

.. _sec:boundaryConditions:

Boundary conditions
=======================

The available boundary conditions (BCs) of temperature and pressure for :code:`HydrothermalSinglePhaseDarcyFoam` are presented below.

.. tip::
    Syntax of all the input files of OpenFOAM, thus of |foam| is C++ style.
    The basic form of a boundary condition can be written as following dictionary structure,

    .. code-block:: cpp

        patchName
        {
            type    boundaryConditionType; //compulsive
            value   flotNumber; //compulsive
            option1 valueOfOption1; //optional
            option2 valueOfOption2; //optional
        }

    where :code:`type` and :code:`value` are always compulsive keys, 
    and sometime the :code:`value` key is just a placeholder but have to be there.
    :code:`option*` represents some optional parameters for a special boundary condition,
    e.g. :code:`qmax` for :code:`HydrothermalHeatFlux` shown blow.

Basic boundary conditions
--------------------------------

.. _sec:BC_empty:

Empty BC: :code:`empty`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The empty BC is used and only applied on non-computed patches for one-dimensional and two-dimensional models. See :numref:`lst:BC_empty` for example.

.. code-block:: cpp
    :caption: Example of empty BC for a 2D model
    :name: lst:BC_empty

    frontAndBack
    {
        type            empty;
    }

.. _sec:BC_fixedValue:

Fixed value BC: :code:`fixedValue`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is the basic and commonly used Dirichlet BC in OpenFOAM, 
:math:`f=f_0\ on\ \partial \Omega`, where :math:`f` denotes some field and :math:`\Omega` represents a boundary patch (*same meaning as belows*).
See :numref:`lst:BC_fixedValue` for example.

.. code-block:: cpp
    :caption: Example of fixedValue BC
    :name: lst:BC_fixedValue

    bottom
    {
        type            fixedValue;
        value           uniform 473.15;//473.15 K = 200 C
    }

.. _sec:BC_fixedGradient:

Fixed gradient: :code:`fixedGradient`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Just like its name, fixedGradient specify a Neumann boundary condition on a patch. 
:math:`\nabla f=g_0\ on\ \partial \Omega`.
See :numref:`lst:BC_fixedGradient` for example.

.. code-block:: cpp
    :caption: Example of fixedGradient BC.
    :name: lst:BC_fixedGradient

    bottom
    {
        type            fixedGradient;
        gradient        0.005; //required
    }

.. _sec:BC_zeroGradient:

Zero gradient: :code:`zeroGradient`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is a special case of :code:`fixedGradient`. 
:math:`\nabla f=0\ on\ \partial \Omega`.
See :numref:`lst:BC_zeroGradient` for example.

.. code-block:: cpp
    :caption: Example of zeroGradient BC for temperature.
    :name: lst:BC_zeroGradient

    right
    {
        type            zeroGradient;
    }

.. tip:: 
    :code:`zeroGradient` **is always applied for permeability**.
    Because permeability is not a primary variable and thus dont't need to solve it.
    But we have to regard it as a field variable just like temperature to initialize the field value, because permeability in our model is not always uniform distribution.
    Therefore we have to specify a boundary condition for permeability.

.. _sec:BC_fixedFluxPressure:

Fixed flux pressure: :code:`fixedFluxPressure`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This boundary condition sets the pressure gradient to the provided value such that the flux on the boundary is that specified by the velocity boundary condition.
This :code:`fixedFluxPressure` BC for pressure :code:`p` is commonly combined with :code:`fixedValue` BC for velocity :code:`U`, 
and of course the velocity field :code:`U` have to be set in :code:`0` folder even though :code:`U` is not a primary variable.
see :numref:`lst:BC_fixedFluxPressure` for example.

.. tip::
    We highly recommend the new defined :code:`noFlux` or :code:`hydrothermalMassFluxPressure` (see :numref:`sec:BC_pressure`, :numref:`sec:BC_hydrothermalMassFluxPressure`) for Neumann boundary condition of pressure.

.. code-block:: cpp
    :caption: Example of fixedFluxPressure BC
    :name: lst:BC_fixedFluxPressure

    right
    {
        type            fixedFluxPressure;
    }

.. _sec:BC_inletOutlet:

Inlet and outlet BC: :code:`inletOutlet`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a generic outflow boundary condition and is commonly applied to temperature :code:`T` at seafloor boundary.
It is a mixed boundary condition that using :code:`zeroGradient` BC when fluid flow out of the boundary and using a :code:`fixedValue` BC when fluid flow into the boundary.
See :numref:`lst:BC_inletOutlet` for example and options.

.. code-block:: cpp
    :caption: Example of inletOutlet BC
    :name: lst:BC_inletOutlet

    top
    {
        type            inletOutlet;
        phi                     phi; //optional
        inletValue      uniform 278.15; //required, fixed value for inflow
        value           uniform 278.15; //required, recommend the same value as inletValue
    }

.. _sec:BC_pressure:

Customized boundary conditions for pressure
----------------------------------------------

The following customized boundary conditions of pressure :code:`p` are designed for seafloor hydrothermal models.

.. _sec:BC_noFlux:

Zero mass flux BC: :code:`noFlux`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This boundary condition is always applied on impermeable insulating boundary, e.g. side wall.
See :numref:`lst:BC_noFlux` for example and options.

.. code-block:: cpp
    :caption: Example of noFlux BC
    :name: lst:BC_noFlux

    left
    {
        type            noFlux;
    }
    right
    {
        type            noFlux;
    }

.. _sec:BC_submarinePressure:

Seafloor BC: :code:`submarinePressure`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a spatial coordinate dependent Dirichlet BC and is derived from :code:`fixedValue` BC.
The pressure boundary value is the hydrostatic pressure on the boundary patch, 
which is calculated from coordinate :math:`y` of the patch.
This is designed for seafloor boundary.
See :numref:`lst:BC_submarinePressure` for example.

.. code-block:: cpp
    :caption: Example of submarinePressure BC
    :name: lst:BC_submarinePressure

    top
    {
        type            submarinePressure;
    }

.. _sec:BC_hydrothermalMassFluxPressure:

Mass flux BC: :code:`hydrothermalMassFluxPressure`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

According Darcy's law :eq:`eq:darcy`, 
gradient of pressure can be expressed by velocity, thus expressed by mass flux.
See :numref:`lst:BC_hydrothermalMassFluxPressure` for example.

.. code-block:: cpp
    :caption: Example of hydrothermalMassFluxPressure BC
    :name: lst:BC_hydrothermalMassFluxPressure

    bottom
    {
        type    hydrothermalMassFluxPressure;
        q       uniform -0.015; // inflow
    }

where :code:`q` in the dictionary denotes mass flux value with unit of :math:`kg/m^2/s`. 
If mass flux represents inflow through the boundary, 
the value is negative, otherwist is positive.

Customized boundary conditions for temperature
--------------------------------------------------

.. _sec:BC_hydrothermalHeatFlux:

Heat flux BC: :code:`hydrothermalHeatFlux`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A commonly used Neumann boundary condition of temperature :code:`T` in hydrothermal modeling is heat flux (:math:`W/m^2`) BC.
For example, it is applied on bottom boundary representing heat source.
A basic example is shown in :numref:`lst:BC_hydrothermalHeatFlux`, 
heat flux on the boundary patch (named :code:`heatsource`) is a constant equal to :math:`5\ W/m^2`.

.. code-block:: cpp
    :caption: Example of hydrothermalHeatFlux BC
    :name: lst:BC_hydrothermalHeatFlux

    heatsource
    {
        type        HydrothermalHeatFlux;
        shape       fixed; //Optional, default is fixed.
        q           uniform 5; //W/m^2
        value       uniform 0; //Placeholder
    }

The :code:`hydrothermalHeatFlux` also support Gaussian shape heat flux, see equation :eq:`eq:gauss_hf` and :numref:`fig:gauss_hf`.

.. math::
    :label: eq:gauss_hf

    q_h(x,z) = q_{min} + (q_{max}-q_{min})e^{-\frac{(x-x_0)^2 + (y-z_0)^2}{2c^2}}

See :numref:`lst:BC_hydrothermalHeatFlux_2D` and :numref:`lst:BC_hydrothermalHeatFlux_3D` for 2D and 3D example, respectively.

.. code-block:: cpp
    :caption: Example of Gaussian shape heat flux BC for 2D model (see also :numref:`fig:gauss_hf`)
    :name: lst:BC_hydrothermalHeatFlux_2D

    bottom
    {
        type        hydrothermalHeatFlux;
        q           uniform 0.05; //placeholder
        value       uniform 0; //placeholder
        shape       gaussian2d;
        x0          0;
        qmax        5;
        qmin        0.05;
        c           500;
    }

.. figure:: /_figures/Gaussian_hf_2d.*
   :width: 500 px
   :align: center
   :name: fig:gauss_hf

   Gaussian shape heat flux curve corresponding to :numref:`lst:BC_hydrothermalHeatFlux_2D`.

.. code-block:: cpp
    :caption: Example of Gaussian shape heat flux BC for 3D model
    :name: lst:BC_hydrothermalHeatFlux_3D

    bottom
    {
        type        hydrothermalHeatFlux;
        q           uniform 0.05; //placeholder
        value       uniform 0; //placeholder
        shape       gaussian2d;
        x0          0;
        z0          0;
        qmax        5;
        qmin        0.5;
        c           500;
    }

Coded boundary conditions
--------------------------------------

The :code:`fixedValue` BC metioned above basiclly specifys a constant boundary condition value.
OpenFOAM provided a so-called dynamic compiling mechanism which allown user define a customized fixed value boundary condition, e.g. a coordinate dependent :code:`fixedValue` BC.

- **Coded fixed value BC**: :code:`codedFixedValue`

.. warning::
    Some programing experience of OpenFOAM, at least C++ is required to use this boundary condition.

An example of a Gaussian shape fixed temperature boundary condition is shown in :numref:`lst:BC_codedFixedValue`.

.. code-block:: bash
    :caption: Example of Gaussian shape fixed temperature (:code:`T`) BC of a 2D model.
    :name: lst:BC_codedFixedValue
    :emphasize-lines: 3,4,5,6,13

    bottom
    {
        type    codedFixedValue;
        value   uniform 873.15; //placeholder
        name    gaussShapeT;
        code    #{
                    scalarField x(this->patch().Cf().component(0)); 
                    double wGauss=200;
                    double x0=1000;
                    double Tmin=573;
                    double Tmax=873.15;
                    scalarField T(Tmin+(Tmax-Tmin)*exp(-(x-x0)*(x-x0)/(2*wGauss*wGauss)));
                    operator==(T);
                #};
    }

The code shown in :numref:`lst:BC_codedFixedValue` implements a Dirichlet boundary condition for temperature :code:`T` which varies along **bottom** boundary with coordinate :math:`x`, the temperature distribution curve is shown in :numref:`fig:gauss_T`. 
In addition, there is also a :code:`codedMixed` BC available for dynamic compiled mixed boundary condition, see `OpenFOAM documentation <https://openfoam.org>`_ for more details. 

.. figure:: /_figures/Gaussian_T_2d.*
   :width: 500 px
   :align: center
   :name: fig:gauss_T

   Gaussian shape temperature curve corresponding to :numref:`lst:BC_codedFixedValue`.

Properties 
================

The parameters in the governing equations can be classified as transport and thermophysical properties.

.. _sec:transportProperties:

Transport properties
--------------------------

The transport properties in |foam| are :code:`porosity`, thermal conductivity :code:`kr` of rock, 
specific heat capacity :code:`cp_rock` of rock, 
density :code:`rho_rock` of rock.
All the transport properties are stored in :code:`constant/transportProperties` file, see :numref:`lst:transportProperties` for example.

.. code-block:: bash
   :emphasize-lines: 10-
   :linenos:
   :caption: Example of transport properties.
   :name: lst:transportProperties

    FoamFile
    {
      version     2.0;
      format      ascii;
      class       dictionary;
      location    "constant";
      object      transportProperties;
    }

    porosity porosity [0 0 0 0 0 0 0] 0.1;
    kr kr [1 1 -3 -1 0 0 0] 2;
    cp_rock cp_rock [0 2 -2 -1 0 0 0] 880;
    rho_rock rho_rock [1 -3 0 0 0 0 0] 2700;


.. note::
    The head (line 1-8 in :numref:`lst:transportProperties`) of the transportProperties file always keep the same, users just need to modify the transport properties (line 10-13 in :numref:`lst:transportProperties`) for a specific hydrothermal system.

.. _sec:thermophysicalProperties:

Thermophysical properties
-------------------------------

The thermophysical properties describe the equation of state (EOS) and thermodynamic properties of a specific fluid, e.g. water.
For single phase hydrothermal circulation modeling, 
we developed a `OpenFOAM thermophysical model <https://cfd.direct/openfoam/user-guide/v6-thermophysical/>`_ (named :code:`htHydroThermo`) of water based on IAPWS-IF97_ and `freesteam-2.1`_ project. 
Similar as other `OpenFOAM thermophysical model <https://cfd.direct/openfoam/user-guide/v6-thermophysical/>`_ for other specific solvers, 
the usage of water :code:`htHydroThermo` is shown in :numref:`lst:thermophysicalProperties`.

.. code-block:: bash
   :emphasize-lines: 12-18
   :linenos:
   :caption: Usage of thermophysical model of :code:`htHydroThermo`.
   :name: lst:thermophysicalProperties

    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        location    "constant";
        object      thermophysicalProperties;
    }

    thermoType
    {
        type            htHydroThermo;
        mixture         pureMixture;
        transport       IAPWS;
        thermo          IAPWS;
        equationOfState IAPWS; //Boussinesq
        specie          specie;
        energy          temperature; //sensibleEnthalpy
    }

    mixture
    {
        specie
        {
            molWeight       18;
        }
    }

.. note::
    :code:`htHydroThermo` is the unique support thermophysical model for solver of :code:`HydrothermalSinglePhaseDarcyFoam` so far. 
    Therefore, **please always copy** :numref:`lst:thermophysicalProperties` **and save it in file of** :code:`constant/thermophysicalProperties`.

.. warning::
    The temperature and pressure limitation of :code:`htHydroThermo` are :math:`[273.15, 1073.15]\ K` and :math:`[10^5, 10^8]\ Pa`, respectively. 
    Please make sure the temperature and pressure field value are in the valid range. 
