.. _SinglePhaseDNSFoam:

.. include:: /include.rst_

.. _model_SinglePhaseDNSFoam:

============================================================================
SinglePhaseDNSFoam
============================================================================

Introduction
==============

**SinglePhaseDNSFoam** -- short for **Single-Phase** **D**\ arcy-**N**\ avier-**S**\ tokes Open\ **FOAM** solver -- 
is a code intended to solver the equations that describe single-phase flow in both porous medium and solid-free region.

.. only:: html

  A 2D demo is shown below.

  .. raw:: html

    <video width=100% autoplay loop>
        <source src="https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/video/SinglePhaseDNSFoam_model_demo.mp4" type="video/mp4">
        Your browser does not support HTML video.
    </video>

.. only:: latex

  A 2D demo is shown in :numref:`fig:SinglePhaseDNSFoam:model:demo`.

  .. figure:: images/SinglePhaseDNSFoam/demo.*
      :align: center
      :name: fig:SinglePhaseDNSFoam:model:demo

      A 2D demo of :ref:`model_SinglePhaseDNSFoam` model.

Theory
=========

The theory of this solver is based on volume averaging principles, where a unique set of partial differential equations is used to represent flow in both regions and scales(see :numref:`fig:SinglePhaseDNSFoam:model:schematic`).
The :ref:`model_SinglePhaseDNSFoam` tends asymptotically towards the Navier-Stokes volume-of-fluid approach in solid-free regions and towards the **single phase** Darcy equations in porous regions.

.. figure:: images/SinglePhaseDNSFoam/Schematic_MultiScalePorousMedium.*
  :align: center
  :name: fig:SinglePhaseDNSFoam:model:schematic

  Schematic representations of a porous medium with two characteristic pore sizes depending on the scale of resolution: (a) full pore scale (Navier- Stokes), (b) intermediate or hybrid scale, and (c) full continuum scale (Darcy). Our objective is to derive a framework that can describe **single phase** flow at all three scales described in the figure based on a single set of equations resolved throughout the entire system. (from :cite:`Carrillo2020`)

Equations
============

* Mass conservation
  
.. math::
  :label: eq:SinglePhaseDNSFoam:mass

  \nabla \cdot \vec{U} = 0

* Momentum conservation

.. math::
  :label: eq:SinglePhaseDNSFoam:momentum

  \underbrace{\frac{1}{\phi} \left( \frac{\partial \rho_f \vec{U}}{\partial t} + \nabla \cdot(\frac{\rho_f}{\phi} \vec{U}\vec{U}) \right)}_{\text{Inertial}} = \underbrace{\nabla \cdot \tau}_{\text{Viscous}} - \underbrace{\frac{\mu}{k}\vec{U}}_{\text{D-B Drag}} -\nabla p + \rho_f \vec{g}

where :math:`\tau = \mu (\nabla \vec{U} + \nabla \vec{U}^T)` is the **shear stress** of incompressible fluid.

* Energy conservation

.. math::
  :label: eq:SinglePhaseDNSFoam:T

  \underbrace{(\varepsilon \rho_f C_{pf} + (1-\varepsilon)\rho_r C_{pr})\frac{\partial T}{\partial t}}_{\text{energy changes}} = \underbrace{\nabla \cdot \left((\varepsilon\lambda_f + (1-\varepsilon)\lambda_r ) \nabla T\right)}_{\text{thermal conduction}} - \underbrace{\rho_f C_{pf} \vec{U}\cdot \nabla T }_{\text{thermal convection}}

Implementations
===================


.. todo::

    完成此求解器的方程分析