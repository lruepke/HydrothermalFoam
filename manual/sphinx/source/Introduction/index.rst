.. _introduction:

*******************
Introduction
*******************

.. include:: /include.rst_

HydrothermalFoam —combination of **hydrothermal** and **OpenFOAM** — 
a three dimensional hydro-thermo-transport model designed to resolvefluid flow within submarine hydrothermal circulation systems. 
HydrothermalFoam has been developed on the OpenFOAM platform, 
which is a Finite Volume based C++ toolbox for fluid-dynamic simulations 
and for developing customized numerical solvers that provides access to 
state-of-the-art parallelized solvers and to a wide range of pre- and post-processing tools. 
We have implemented a porous media Darcy-flow model with associated boundary conditions designed to facilitate numerical 
simulations of submarine hydrothermal systems. 
The current implementation is valid for single-phase fluid states and uses a pure water equation-of-state (IAPWS-97). 
We here present the model formulation, OpenFOAM implementation details, and a sequence of 1-D, 2-D and 3-D benchmark tests. 
The source code repository further includes a number of tutorials that canbe used as starting points 
for building specialized hydrothermal flow models. 

Features
===============
Features of the |foam| are summarized as following:

- **Original characteristics of OpenFOAM**: |foam| keeps all the original characteristics of OpenFoam, for example, file structure of case, syntax of all the input files and output files, mesh, utilities, even part of varable names in the source code are kept the same. This principle has two advantages, one is that it is easy to understand and to use |foam| if you are a OpenFoam user. The other is that it is easy to compar and understand |foam| solver and the other standard solvers in OpenFoam.

- **Mesh**: HydrothermalFoam supports both structured regular mesh and unsructured mesh. The internal structured regular mesh tool, :code:`blockMesh`, is recommended for new users. While Gmsh_ is also an excellent open source unstuctured mesh generator, and there is a utility named :code:`gmshToFoam` can transfoam gmsh to OpenFoam mesh.

- **Boundary conditions**: even though OpenFoam has a lot of build-in boundary conditions, we also developed some specific boundary conditions, e.g. :code:`noFlux`, :code:`HydrothermalHeatFlux` for the specific problem — Hydrothermal system.


Information
=================

.. - Development team: `Zhikui Guo <https://orcid.org/0000-0002-0604-0455>`_ , `Lars Rüpke <https://orcid.org/0000-0001-7025-4362>`_

- License: `GNU GeneralPublic License v3.0 <https://gitlab.com/gmdpapers/hydrothermalfoam/-/blob/master/LICENSE>`_

- Software doi: `10.5281/zenodo.3755648 <https://doi.org/10.5281/zenodo.3755648>`_

- GitLab repository: `https://gitlab.com/gmdpapers/hydrothermalfoam <https://gitlab.com/gmdpapers/hydrothermalfoam>`_ 

- Docker Hub repository: `zguo/hydrothermalfoam <https://hub.docker.com/repository/docker/zguo/hydrothermalfoam>`_

Dependent package
=====================

- OpenFOAM_

- freesteam_

- Gmsh_
