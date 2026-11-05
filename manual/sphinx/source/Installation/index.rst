.. _installation:


*******************
Installation
*******************

.. include:: /include.rst_

.. tip::

   We provide a 5-minutes quick start video (on Mac OS) that can be accessed here `https://youtu.be/6czcxC90gp0 <https://youtu.be/6czcxC90gp0>`_.
   

There are two ways to install |foam|. 
The easiest way is intalling via Docker image, see :numref:`sec:install_docker`.
Another way is building from source code if user has experience of OpenFOAM installation, see section of `Build from source`_.


.. _sec:install_docker:

Docker image
===================
For users who do not run Ubuntu Linux, we provide a pre-compiled Docker image,
`lruepke/hydrothermalfoam-openfoam10 <https://hub.docker.com/r/lruepke/hydrothermalfoam-openfoam10>`_,
for Intel/AMD (amd64) and ARM/Apple Silicon (arm64) computers.
It contains OpenFOAM 10 (Foundation version) on Ubuntu 22.04, |foam| with the solver :code:`HTFoam`,
and xThermo, the H\ :sub:`2`\ O-NaCl equation of state, including its Python API.

1. **Install** `Docker Desktop <https://www.docker.com/products/docker-desktop>`_ and keep it running.

2. **Create a container** from the image. The folder :code:`HydrothermalFoam_runs` in your home directory is shared between your computer and the container:

   .. code-block:: bash

      docker run -it --name hydrothermalfoam \
          -v "$HOME/HydrothermalFoam_runs:/home/openfoam/HydrothermalFoam_runs" \
          lruepke/hydrothermalfoam-openfoam10:latest

   Docker downloads the image the first time and opens a shell in the container. Use a fixed version (e.g. :code:`:2026.10`) instead of :code:`:latest` when everyone in a course or project should have the same setup.

3. **Get back into the container** later with :code:`docker start -ai hydrothermalfoam`.

You are now in an Ubuntu Linux environment with OpenFOAM and |foam| ready to use.
We recommend running |foam| cases in the directory :code:`HydrothermalFoam_runs` in the container.
The results are then also in the shared folder on your computer,
and can be visualized with ParaView_, Tecplot_ or other CFD post-processing software.

.. tip::

   For courses, there is also a teaching image,
   `lruepke/hydrothermalfoam-teaching <https://hub.docker.com/r/lruepke/hydrothermalfoam-teaching>`_,
   which adds a Python environment, JupyterLab and Visual Studio Code that are used in the web browser.


Build from source
==========================

Install OpenFOAM
------------------------

The |foam| v1.0 is developed based on OpenFOAM-7, which can be installed according to the installation instructions (https://openfoam.org/download/) given by the development team for 
`Ubuntu Linux <https://openfoam.org/download/7-ubuntu/>`_, 
`Other Linux <https://openfoam.org/download/7-linux/>`_, 
`macOS <https://openfoam.org/download/7-macos/>`_ and `Windows <https://openfoam.org/download/windows-10/>`_ platform, respectively.

Build HydrothermalFoam
----------------------------

Once OpenFOAM is built successfully, 
the source code of |foam| be downloaded 
from `Zenodo <https://doi.org/10.5281/zenodo.3755648>`_ or 
from `GitLab repository <https://gitlab.com/gmdpapers/hydrothermalfoam>`_. 
The directory structure and components ofHydrothermalFoamare shown in :numref:`fig_file_structure_main` and the components canbe built follow three steps below,

.. figure:: /_figures/filetree_main.*
   :width: 500 px
   :align: center
   :name: fig_file_structure_main

   Structure and components of the |foam| toolbox.

.. note::

   The following steps are only proper for Mac OS and Linux systems, 
   we do not yet build HydrothermalFoam on Windows system directly.
   If users using ubuntu sub-system on Windows 10, 
   the following steps could work in the sub-system.

1. **Build freesteam-2.1 library**. The freesteam project is constructed by scons_, which is a open source software constructiontool dependent on `python 2`_, and based on GSL_ (GNUScientificLibrary). Therefore python 2, scons and GSL have to be installed firstly, then change directory to freesteam-2.1 in HydrothermalFoam source code and type command of :code:`scons INSTALL_PREFIX=$FOAM_USER_LIBBIN install` to compile freesteam library named :code:`libfreesteam.so`. See home page of freesteam-2.1_ project for more details.

2. **Build libraries of customized boundary conditions and thermo-physical model**. Change directory to libraries and type command of :code:`./Allmake` to compile the libraries named :code:`libHydroThermoPhysicalModels.so, libHydrothermalBoundaryConditions.so`.

.. warning::

   It should be noted that if you are using OpenFOAM-8, you have to run `./Allmake-8` to compile thermo-physical model to compatible with OpenFOAM-8. And of course the `Allmake` script is designed for OpenFOAM-7. **This is the only difference between version 7 and version 8.**

3. **Build solver of HydrothermalSinglePhaseDarcyFoam**. Change directory to HydrothermalSinglePhaseDarcyFoam and type command of :code:`wmake` to compile the solver named :code:`HydrothermalSinglePhaseDarcyFoam`.

.. note::

   All the library files and executable application (solver) file will be generated in directories defined by OpenFOAM’s path variables of :code:`FOAM_USER_LIBBIN` and :code:`FOAM_USER_APPBIN`, respectively. 
   If build HydrothermalFoam in Mac OS, the extension of the library files is :code:`.dylib`, 
   please make a symbolic links. 
   For example, see following command for :code:`libHydroThermoPhysicalModels.dylib` 

   .. code-block:: bash

      ln -s $FOAM_USER_LIBBIN/libHydroThermoPhysicalModels.dylib $FOAM_USER_LIBBIN/libHydroThermoPhysicalModels.so