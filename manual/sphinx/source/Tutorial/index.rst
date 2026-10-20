.. _tutorial:

*******************
Tutorial
*******************
 
.. include:: /include.rst_

Usage of |foam| tool is similar to any other solver of OpenFOAM, 
see OpenFOAM :download:`user guide <http://foam.sourceforge.net/docs/Guides-a4/OpenFOAMUserGuide-A4.pdf>` for more details.
The basic usage of |foam| are shown as below.


.. _sec:meshing:

Mesh generation
====================

The are several ways to generat mesh, including OpenFOAM's built-in :code:`blockMesh` application for generating meshes of simple geometries, 
:code:`snappyHexMesh` application for meshing complex geometries and 
applications that convert meshes from well known formats into the OpenFOAM format, e.g. :code:`fluentMeshToFoam`, :code:`gmshToFoam`.
see OpenFOAM user guide-`mesh generation and conversion <https://cfd.direct/openfoam/user-guide/v7-mesh/>`_ for details.

This section we simply present how to use :code:`blockMesh` and :code:`gmshToFoam` for generating mesh and defining boundary patches.

.. _sec:meshing_blockMesh:

Simple mesh generation: :code:`blockMesh`
----------------------------------------------

The mesh is generated from a dictionary file named :code:`blockMeshDict` located in the :code:`system` directory of a case. :code:`blockMesh` reads this dictionary, generates the mesh and writes out the mesh data 
to :code:`points` and :code:`faces`, 
:code:`cells` and :code:`boundary` files in the :code:`constant/polyMesh` directory (see :numref:`fig:case_structure_main`).

:code:`blockMesh` decomposes the domain geometry into a set of 1 or more three dimensional, hexahedral blocks. 
Each block of the geometry is defined by 8 vertices, one at each corner of a hexahedron. 
An simple example block and vertices numbering is shown in :numref:`fig:blockMesh`.
The vertices are written in a list so that each vertex can be accessed using its label, 
remembering that OpenFOAM always uses the C++ convention that the first element of the list has label ‘0’. 


.. figure:: /_figures/blockMesh.*
   :align: center
   :name: fig:blockMesh
   :width: 50 %

   The coordinate system and vertices numbering of single block for :code:`blockMesh`.

An example of :code:`blockMeshDict` for describing a 2D box is shown in :numref:`lst:blockMeshDict`.
The key entries are :code:`vertices`, :code:`blocks` and :code:`boundary`.

- **vertices** contains all three-dimension coordinate of each vertex (line 15-25), e.g. vertex 0 is :code:`(0 $ymin 0)` and the vertex 5 is :code:`($Lx $ymin $Lz)`, the coordinate system is shown in :numref:`fig:blockMesh`.

- **blocks** contains vertex connection of a hexahedron, numbers of cells in each direction and cell expansion ratios. The order of vertex connection is :code:`(0 1 2 3 4 5 6 7)`. :code:`(100 50 1)` means the number of cells in :math:`x`, :math:`y` and :math:`z` direction will be 100, 50 and 1 (for 2D case), respectively. :code:`simpleGrading` is typically set to :code:`(1 1 1)`, see OpenFOAM user gide-`blockMesh <https://cfd.direct/openfoam/user-guide/v7-blockMesh/>`_ for more details.

- **boundary** contains sub-dictionarys for defining boundary patches. The name (e.g. :code:`right` or whatever the user like) of the sub-dictionary is the boundary patch name which will be used in filed data (see :numref:`sec:boundaryConditions`). There are two key entries, :code:`type` and :code:`faces` in each sub-dictionary. The :code:`type` is typically set to :code:`patch` or :code:`empty` for a non-computing boundary patch of a non-three-dimensional case. :code:`faces` is a list of block faces that make up the patch with a user defined name (see lines 43-46 for :code:`right` patch or lines 67-71 for :code:`frontAndBack` patch shown as transparent surface in :numref:`fig:blockMesh`)
 
.. literalinclude:: /../../../cookbooks/2d/Regular2DBox/system/blockMeshDict
   :language: foam
   :linenos:            
   :lines: 8- 
   :emphasize-lines: 5-6,10
   :caption: Example of :code:`blockMeshDict` for a 2D box.
   :name: lst:blockMeshDict
  
.. tip::
   We can also use variable in :code:`blockMeshDict`. 
   For example :code:`ymin -3000;`, it should be noted that there is no :code:`=` between variable name and value, 
   and :code:`;` is required. 
   In addition, the :code:`convertToMeters` keyword specifies a scaling factor by which all vertex coordinates in the mesh description are multiplied, e.g. `convertToMeters 0.01;` scales to mm.

   Then just type :code:`blockMesh` command in the terminal in the root directory of the case after finishing :code:`blockMeshDict`.

.. _sec:meshing_gmsh:

Convert gmsh to OpenFOAM: :code:`gmshToFoam`
-----------------------------------------------

The OpenFOAM built-in meshing utility, :code:`blockMesh`, can generate some simple mesh, 
but it is difficulty to describe complex geometry in :code:`blockMeshDict` dictionary file.
In this section, we introduce how to use gmsh_ to generate mesh and then use :code:`gmshToFoam` convert the mesh to OpenFOAM format.

.. _sec:gmsh_geometry_boundary:

Create geometry and define boundary patches 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here we present a example for creating 2D and 3D box geometry, and defining boundary patches.
See `gmsh manual <https://gmsh.info/doc/texinfo/gmsh.html>`_ 
(:download:`pdf <https://gmsh.info/doc/texinfo/gmsh.pdf>`) 
for more details about geometry definition and mesh generation.

- **Geometry description**

The geometry descriptions are stored in a gmsh geometry script file with extension :code:`.geo`.
Gmsh script files support both C and C++ style comments and the syntax is similar to C/C++ as well.
The user can use gmsh GUI to create a geometry script file, 
and also can write the geometry script file directly in your favorive text editor, 
e.g. `Visual Stuio Code <https://code.visualstudio.com>`_ with 
`gmsh extension <https://marketplace.visualstudio.com/items?itemName=Bertrand-Thierry.vscode-gmsh>`_.
An gmsh geometry script file of a 3D box is shown in :numref:`lst:3Dbox_geo` 
(:download:`box.geo <https://gitlab.com/gmdpapers/hydrothermalfoam/-/tree/master/cookbooks/2d/gmsh2DBox/gmsh/box.geo>`).

.. literalinclude:: /../../../cookbooks/2d/gmsh2DBox/gmsh/box.geo
   :language: gmsh  
   :linenos:  
   :lines: 1-27
   :emphasize-lines: 23-27
   :caption: Example of gmsh geometry script of a 3D box.
   :name: lst:3Dbox_geo

The geometry script file can be opened and visualized by gmsh GUI, see :numref:`fig:box_geo_gmsh_gui`. 
Gmsh supports three-dimensional interactive operation and there are mouse tooltips of 
number and other informations for each point, line, surface and volume.
Therefor the user can easily get the number of each boundary patch and volume (cell region).

.. figure:: /_figures/box_geo_gmsh_gui.png
   :align: center
   :name: fig:box_geo_gmsh_gui

   Gmsh GUI display a 2D box geometry.

- **Boundary patches and cell regions definition**

The user can specify a specific name, e.g. :code:`bottom`, for each :code:`Surface` (gmsh keyword) or a name for boundary patches group, 
e.g. :code:`frontAndBack`. 
These boundary patches name will be used to specify boundary conditions in field data file(see :numref:`sec:boundaryConditions`).
In addition, the user can also specify specific name for each :code:`Volume` (gmsh keyword).
This volume name will be used to set field distribution, e.g. permeability (see :numref:`sec:setFields`).
The specification of boundary pathch name and cell region name can be done by :code:`Physical` keyword, see :numref:`lst:3Dbox_geo_boundary`.

.. literalinclude:: /../../../cookbooks/2d/gmsh2DBox/gmsh/box.geo 
   :language: gmsh
   :linenos:
   :lines: 28-35
   :caption: Example of boundary patch definition in gmsh geometry script.
   :name: lst:3Dbox_geo_boundary

.. tip::
   Gmsh will specify some default colors for every surfaces and volumes.
   The user can also set specific color for each pathch and volume (see blow) to check boundary mesh.
   
   .. literalinclude:: /../../../cookbooks/2d/gmsh2DBox/gmsh/box.geo
      :language: gmsh
      :linenos:
      :lines: 36-

Generate mesh 
^^^^^^^^^^^^^^^^^^^

.. figure:: /_figures/box_msh_gmsh_gui.png
   :align: center
   :name: fig:box_msh_gmsh_gui

   Gmsh GUI display a 2D box mesh.

Mesh generation process is pretty easy, the user can do it using gmsh GUI :guilabel:`Mesh` -> :guilabel:`3D`.
The mesh result is shown in :numref:`fig:box_msh_gmsh_gui`.
Because :code:`gmshToFoam` in OpenFOAM-7 can only read gmsh :code:`.msh` file in format of version 2, 
the user have to export (:guilabel:`File` -> :guilabel:`Export` -> :guilabel:`Gmsh MESH`) the mesh file to  **Version 2 ASCII** format (see :numref:`fig:gmsh_save_gui`).

.. figure:: /_figures/gmsh_save_gui.png
   :align: center
   :name: fig:gmsh_save_gui
   :width: 30 %

   Export msh to Version 2.

Alternately, the mesh generation and save file can be done by a single line of command (see :numref:`lst:gmsh_meshing_save`)

.. code-block:: bash
   :name: lst:gmsh_meshing_save
   :caption: Meshing and saving command of gmsh.

   gmsh gmsh/mesh.geo -3 -o gmsh/mesh.msh -format msh22`.

.. _sec:convertGmsh:

Convert mesh 
^^^^^^^^^^^^^^^^^^^

If the mesh file is generated successfully, 
the user can convert the mesh to OpenFOAM format by running command of :code:`gmshToFoam mymesh.msh` in the root directory of a case.
Then a directory named :code:`polyMesh` will be generated in :code:`constant` directory.
All the defined boundary patches are converted to :code:`polyMesh/boundary` file (see :numref:`lst:gmsh_convert_boundary`).
If the case is three-dimensional, now the mesh generation process is done.
But for 2D case, the user have to set :code:`empty` boundary pathches by modifying the :code:`boundary` file directly.

.. code-block:: bash
   :name: lst:gmsh_convert_boundary
   :caption: :code:`polyMesh/boundary` converted by :code:`gmshToFoam`.

   5
   (
      frontAndBack
      {
         type            patch;
         physicalType    patch;
         nFaces          6240;
         startFace       4600;
      }
      left
      {
         type            patch;
         physicalType    patch;
         nFaces          20;
         startFace       10840;
      }
      top
      {
         type            patch;
         physicalType    patch;
         nFaces          60;
         startFace       10860;
      }
      right
      {
         type            patch;
         physicalType    patch;
         nFaces          20;
         startFace       10920;
      }
      bottom
      {
         type            patch;
         physicalType    patch;
         nFaces          60;
         startFace       10940;
      }
   )


.. tip::
   We provide a python script (:download:`setEmptyPatch.py <https://gitlab.com/gmdpapers/hydrothermalfoam/-/blob/master/benchmarks/HydrothermalFoam/2d/setEmptyPatch.py>`) to modify a boundary patch to :code:`empty` by patch name.
   For example, set :code:`frontAndBack` patches to :code:`empty` by running the following command at case root directory.

   .. code-block:: bash 

      python setEmptyPatch.py frontAndBack

.. _sec:case_setup:

Case setup
==================

A model case of |foam| basically consists of 
**time directory** (e.g. :code:`0` for initial state), 
**constant** and **system** directory (see :numref:`fig:case_structure_main`).
The sub-directory of **polyMesh** in **constant** folder consists mesh files, 
which are generated by meshing utility, 
e.g. :code:`blockMesh`, :code:`gmshToFoam`, 
:code:`snappyHexMesh`,..., 
see :numref:`sec:meshing`.

.. figure:: /_figures/casetree_main.*
   :align: center
   :name: fig:case_structure_main

   Directory structure of a case of |foam|.

.. _sec:initial:

Initial state
------------------

The field data files of initial state are commonly stored in :code:`0` time directory.
Of course it can be another time directory, e.g. :code:`1000`, 
which is specified by key of :code:`startFrom` in :code:`controlDict` in :code:`system` directory (see :numref:`sec:system`).
In the initial state directory, the field file of primary variable :code:`T, p` and :code:`permeability` are compulsive, 
and :code:`U` is also required if :code:`fixedFluxPressure` is applied on a boundary patch for pressure (see :numref:`sec:BC_fixedFluxPressure`). 
An example field data file of :code:`T` is shown in :numref:`lst:case_T`, 
which is a basic structure of dictionary file of a field data.
A field data file basicly contains its 
**variable type** (line 5), 
**object name** (line 6), 
**dimension** (line 9), 
**internal filed** value (line 10) and 
**boundary field** value (boundary conditions, line 11-42).


.. code-block:: cpp
   :emphasize-lines: 5,6,9-11,21-25
   :linenos:
   :caption: Example field data of temperature.
   :name: lst:case_T

   FoamFile
   {
      version     2.0;
      format      ascii;
      class       volScalarField;
      object      T;
   }

   dimensions      [0 0 0 1 0 0 0];
   internalField   uniform 278.15;     //5 C
   boundaryField
   {
      left
      {
         type            zeroGradient;
      }
      right
      {
         type            zeroGradient;
      }
      top
      {
         type        fixedValue;
         value       uniform 278.15;
      }
      bottom
      {
         type              hydrothermalHeatFlux;
         q                 uniform 0.05;
         value             uniform 0;
      }
      heatsource
      {
         type              hydrothermalHeatFlux;
         q                 uniform 5;
         value             uniform 0;
      }
      frontAndBack
      {
         type            empty;
      }
   }

- **Variable type** (:code:`class`) and **object name** (:code:`object`). See |paper_hydrothermalfoam| for variable type and object name index.

- **Internal field** (:code:`internalField`) can be set as uniform (just like line 10 in :numref:`lst:case_T`) or non-uniform (see :numref:`sec:setFields`).

- **Boundary conditions** (:code:`boundaryField`). The boundary patch name, e.g. :code:`bottom`, is defined in mesh file of *constant/polyMesh/boundary* (see :numref:`fig:case_structure_main` and :numref:`sec:meshing`). The available boundary conditions and their usage can be found in :numref:`sec:boundaryConditions`.

.. tip::
   To avoid making mistakes, user should copy the field data files form any case in cookbooks_ or benchmarks_ and then make some changes.

.. _sec:constant:

Constant 
--------------

For |foam|, the constant directory always contains three files named :code:`g`, :code:`thermophysicalProperties`, :code:`transportProperties` respectively, and one folder named :code:`polyMesh` (see :numref:`fig:case_structure_main`).

- **g** contains gravitational acceleration constant. It is same for basically all cases of OpenFOAM-based solvers. Therefor, please just copy this file from any existed case to a new case.

- **thermophysicalProperties** contains thermophysical model. It is the same for all cases of HydrothermalSinglePhaseDarcyFoam solver, see :numref:`sec:thermophysicalProperties`.

- **transportProperties** contains constant parameters about transport, see :numref:`sec:transportProperties`.

- **polyMesh** directory contains necessary mesh files which are automatically generated by meshing utility, e.g. :code:`blockMesh`, :code:`gmshToFoam` (see :numref:`sec:meshing`).

.. _sec:system:

System
------------

As shown in :numref:`fig:case_structure_main`, 
the **system** directory contains three compulsive directory files of 
**controlDict**, **fvSchemes** and **fvSolution**, and optional dictionary file, 
e.g. **blockMeshDict** for OpenFOAM built-in meshing utility :code:`blockMesh`.

Time and data input/output control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The **controlDict** dictionary sets time and data input/output control, 
the commonly used entries for *HydrothermalSinglePhaseDarcyFoam* solver are shown in :numref:`lst:controlDict`.
See OpenFOAM user guide-`controlDict <https://cfd.direct/openfoam/user-guide/v7-controldict/>`_ for more details of each entry.
A few entries that need to be emphasized are highlighted in the :numref:`lst:controlDict`.

- **application** specifies solver name, which should be `HydrothermalSinglePhaseDarcyFoam`.

- **libs** contains some shared libraries using in the case. These three libraries listed in **lines 46-48** must be inlcuded in **libs** sub-dictionary for customized thermophysical model and boundary conditions.

.. literalinclude:: /../../../cookbooks/2d/Regular2DBox/system/controlDict
   :language: foam
   :linenos:
   :lines: 8- 
   :emphasize-lines: 9, 27-32
   :caption: Example entries from a :code:`controlDict` dictionary.
   :name: lst:controlDict

.. note::
   There are three options (:code:`firstTime, startTime, latestTime`) available for the :code:`startFrom` keyword entry.
   :code:`startTime` specifies start time for the simulation when :code:`startFrom startTime;`.

Numerical schemes
^^^^^^^^^^^^^^^^^^^^

The :code:`fvSchemes` dictionary in the :code:`system` directory sets the numerical schemes for terms, 
such as derivatives in equations, that are calculated during a simulation. 
The commonly used entries of :code:`fvSchemes` for :code:`HydrothermalSinglePhaseDarcyFoam` solver are shown in :numref:`lst:fvSchemes`.
See OpenFOAM user guide-`fvSchemes <https://cfd.direct/openfoam/user-guide/v7-fvSchemes/>`_ for more available scheme options of each terms.

As shown in :numref:`lst:fvSchemes`, 
user have to specify numerical scheme for transient (lines 11-14), 
gradient of pressure :code:`p` (line 19) and temperature :code:`T` (line 20), 
laplacian terms (line 33-34), surface interpolation (lines 37-40), surface gradient (lines 42-45).
In addition, the :code:`fluxRequired` sub-dictionary have to be specified for reconstructing Darcy velocity from flux after solving pressure. 
See **Model development** section in |paper_hydrothermalfoam| 
or `source code of the solver <https://gitlab.com/gmdpapers/hydrothermalfoam/-/tree/master/solvers/HydrothermalSinglePhaseDarcyFoam>`_ 
for more detail implementation of each terms.

.. literalinclude:: /../../../cookbooks/2d/Regular2DBox/system/fvSchemes
   :language: foam
   :linenos:
   :lines: 8- 
   :emphasize-lines: 17,18,23,24,29,30,40-44
   :caption: Example entries from a :code:`fvSchemes` dictionary.
   :name: lst:fvSchemes

.. tip::
   The basic numerical schemes of :code:`HydrothermalSinglePhaseDarcyFoam` solver are shown in :numref:`lst:fvSchemes`, 
   user can use other available schemes of each term (see OpenFOAM-`fvSchemes <https://cfd.direct/openfoam/user-guide/v7-fvSchemes/>`_), 
   e.g. :code:`Gauss vanLeer` for :code:`div(phi,T)`.

Solution and algorithm control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The equation solvers, tolerances and algorithms are controlled from the :code:`fvSolution` dictionary 
in the :code:`system` directory. 
An example set of entries from the :code:`fvSolution` dictionary required 
for the :code:`HydrothermalSinglePhaseDarcyFoam` solver is shown in :numref:`lst:fvSolution`.
See OpenFOAM user guide-`fvSolution <https://cfd.direct/openfoam/user-guide/v7-fvSolution/>`_ for more details of each entry.

As shown in :numref:`lst:fvSolution`, 
user have to specify linear equations :code:`solver`, :code:`preconditioner`, :code:`tolerance` and :code:`relTol` 
for pressure  and temperature in sub-dictionary of :code:`p` and :code:`T`, respectively.
In addition, a sub-dictionary named in format of :code:`*Final` is required as well (see lines 20-24 and 32-36). 
The prefix of :code:`*` denotes primary variable name, e.g. :code:`p` for pressure.
The key entry :code:`relTol` is typically set to 0.
For :code:`HydrothermalSinglePhaseDarcyFoam` solver, key entry :code:`PIMPLE` is also required besides :code:`solvers`, 
because we adopt :code:`pimple.correctNonOrthogonal()` for non-orthogonal correction.
The key entry :code:`nNonOrthogonalCorrectors` in :code:`PIMPLE` dictionary specifies repeated solutions of the pressure equation, 
used to update the explicit non-orthogonal correction of Laplacian term (see OpenFOAM user guide-`Surface normal gradient schemes <https://cfd.direct/openfoam/user-guide/v7-fvSchemes/#x20-1490004.5.4>`_ for more details).
:code:`nNonOrthogonalCorrectors` is typically set to 0 or 1.

.. literalinclude:: /../../../cookbooks/2d/Regular2DBox/system/fvSolution
   :language: foam
   :linenos:
   :lines: 8- 
   :emphasize-lines: 37-40
   :caption: Example entries from a :code:`fvSolution` dictionary.
   :name: lst:fvSolution

.. warning::
   The entries and values shown in :numref:`lst:fvSolution` are the recommended options, 
   it is unnecessary to modify them unless the user understands the source code of the solver and OpenFOAM and then wants to test other available parameters of :code:`fvSolution`.

.. _sec:setFields:

Set fields
==============

The user can set a specific value for a field(e.g. :code:`permeability`) in a specific cell region using utility :code:`setFields`,
which reads dictionary file :code:`setFieldsDict` in :code:`system` directory.
An example of :code:`setFieldsDict` is shown in :numref:`lst:setFieldsDict` (see :numref:`sec:cookbooks_pipe`).

.. literalinclude:: /../../../cookbooks/pipe_3D/system/setFieldsDict
   :language: cpp
   :linenos:
   :lines: 8-
   :caption: Example of :code:`setFieldsDict` file.
   :name: lst:setFieldsDict

The option (e.g. :code:`layer2A` in line 17) of key entry :code:`name` in :code:`zoneToCell` sub-dictionary in :numref:`lst:setFieldsDict` is defined as :code:`Physical Volume("xxx")={...};` in gmsh geometry (:code:`.geo`) file (see :numref:`sec:gmsh_geometry_boundary`).
Another commonly used key entry is :code:`boxToCell` which sets field value in a box 
defined by the two ends of the diagonal, see :numref:`lst:setFieldsDict_boxToCell`.

.. code-block:: cpp
   :linenos:
   :caption: Example of :code:`boxToCell` in :code:`setFieldsDict` file.
   :name: lst:setFieldsDict_boxToCell

   regions
   (
      boxToCell
      {
         box (0 0 0) (10 10 10);
         fieldValues
         (
            volScalarFieldValue permeability 4e-14
         );
      }
   )

.. _sec:runCase:

Run Case
==========

The user can run a case just by running command of :code:`HydrothermalSinglePhaseDarcyFoam` in the root directory of a case.
But several processes metioned above, 
e.g. mesh generation and/or mesh conversion, 
empty boundary type modification, 
case setup and initial field setting,
have to be done before running a case.
All the pre-processing steps can be assembled into a bash file, 
e.g. :download:`run.sh <https://gitlab.com/gmdpapers/hydrothermalfoam/-/blob/master/cookbooks/2d/pipe/run.sh>` shown in :numref:`lst:run.sh`. 


.. literalinclude:: /../../../cookbooks/pipe/run.sh
   :language: bash
   :linenos:
   :lines: 1-
   :emphasize-lines: 20, 22-25
   :caption: Example of command set(:code:`run.sh`) to run a case.
   :name: lst:run.sh

.. literalinclude:: /../../../cookbooks/pipe/clean.sh
   :language: bash
   :linenos:
   :lines: 1-
   :caption: Example of command set(:code:`clean.sh`) to clean a case.
   :name: lst:clean.sh

.. note::

   If the user want to run a case in parallel, 
   just need to comment line 20 in :numref:`lst:run.sh` and uncomment lines 23-25 in :numref:`lst:run.sh`.
   In addition, the user have to setup the :download:`decomposeParDict <https://gitlab.com/gmdpapers/hydrothermalfoam/-/blob/master/cookbooks/2d/pipe/system/decomposeParDict.orig>` dictionary file in :code:`system` directory (see :numref:`lst:decomposeParDict` for example).
   See `OpenFOAM user guide <https://cfd.direct/openfoam/user-guide/v6-running-applications-parallel/>`_ for more details about parallel computing.

.. literalinclude:: /../../../cookbooks/3Dbox_par/system/decomposeParDict
   :language: foam
   :linenos:
   :lines: 8-
   :caption: Example of :code:`decomposeParDict` dictionary file.
   :name: lst:decomposeParDict

.. note::

   It is of course possible to set up input files for cases completely from scratch. 
   However, in practice, it is often simpler to go through the list of cookbooks_ already provided 
   and find one that comes close to what you want to do. 
   You would then modify this cookbook until it does what you want to do. 
   The advantage is that you can start with something you already know works, 
   and you can inspect how each change you make – 
   changing the details of the geometry, 
   changing the boundary conditons, 
   or changing initial field distribution – affects what you get.

.. _sec:post-processing:

Post-processing and visualization
======================================

The commonly used post-processing tool is ParaView_.
There is a built-in utility :code:`paraFoam`, which is based on ParaView, can read and render generic results of OpenFOAM case.
The user can run the :code:`paraFoam` command in the root directory of case direction, 
or run command of :code:`paraFoam -case <caseDir>` in any other directory.

.. tip::

   The new version (e.g. 5.5.0) of ParaView_ has OpenFOAM case reader which will read a file with extension of :code:`.foam` in the root directory of a case.
   Therefore, if the user install OpenFOAM or HydrothermalFoam tool via Docker (see :numref:`sec:install_docker` and `video <https://youtu.be/6czcxC90gp0>`_), 
   the results can be visualized in host through the shared folder.
   The results will saved in the shared folder when running a case in the container, 
   and then create a empty file with extension of :code:`.foam`, e.g. :code:`results.foam`, in the shared folder.
   The user can open file :code:`results.foam` in the shared folder in host by ParaView to display the results.