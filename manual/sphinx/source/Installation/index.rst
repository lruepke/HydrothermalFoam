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
In order to quick start to use |foam| for non-Ubuntu users, 
we provided a pre-compiled docker image which can be found on `Docker Hub <https://hub.docker.com/repository/docker/zguo/hydrothermalfoam>`_ repository,
named `zguo/hydrothermalfoam <https://hub.docker.com/repository/docker/zguo/hydrothermalfoam>`_.
It's pretty simple to install |foam| via Docker, all the steps are summarized below,

1. **Install** `Docker desktop <https://www.docker.com/products/docker-desktop>`_ and keep it running.

2. **Pull** the docker image of |foam| by running command of :code:`docker pull zguo/hydrothermalfoam`.

3. **Install a container** from the docker image by running shell script which can be fond in source code directory of `docker <https://gitlab.com/gmdpapers/hydrothermalfoam/-/tree/master/docker>`_ (see also :numref:`lst_docker_mac` and :numref:`lst_docker_win`). The :code:`HydrothermalFoam_runs` directory is a shared folder between the container and host machine. 

.. literalinclude:: /../../../docker/installMacHydrothermalFoam.sh
   :language: bash
   :emphasize-lines: 15
   :linenos:
   :lines: 29-
   :caption: Script for Mac OS (`installMacHydrothermalFoam.sh <https://gitlab.com/gmdpapers/hydrothermalfoam/-/blob/master/docker/installMacHydrothermalFoam.sh>`_)
   :name: lst_docker_mac

.. literalinclude:: /../../../docker/installWindowsHydrothermalFoam.ps1
   :language: bat
   :emphasize-lines: 15
   :linenos:
   :lines: 29-
   :caption: Script for Windows (`installWindowsHydrothermalFoam.ps1 <https://gitlab.com/gmdpapers/hydrothermalfoam/-/blob/master/docker/installWindowsHydrothermalFoam.ps1>`_)
   :name: lst_docker_win

4. **Start the container** by running command of :code:`docker start hydrothermalfoam`.

5. **Attach the container** by running command of :code:`docker attach hydrothermalfoam`. 

The user now in a Ubuntu linux environment with precompiled HydrothermalFoam tools which located at directory of :code:`~/HydrothermalFoam`.
We recommend user run HydrothermalFoam cases in the directory of :code:`HydrothermalFoam_runs` in the container, 
and then the results are synchronized in the shared directory in the host, 
and thus can be visualized by ParaView_, Tecplot_ or other CFD post-processing software.


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