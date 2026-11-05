.. _index_helloworld:

.. include:: /include.rst_

.. _cookbook_helloworld:

Hello World: 2D box
----------------------

All the input files can be found in |helloworld| directory.

This is the firs simplest example to show the basic steps to run a case.
The geometry and boundary conditions are shown in figure :numref:`fig:geometry_2Dbox`.
The following steps present how to setup a case from scratch, 
see `helloworld <https://gitlab.com/gmdpapers/hydrothermalfoam/-/tree/master/cookbooks/helloworld>`_ case.

.. figure:: /_figures/model_helloworld.*
   :align: center
   :name: fig:geometry_2Dbox

   The geometry and boundary conditions of the 2D box model.

Step 1: create :code:`controlDict` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First thing we have to do is create a case directory, e.g. named :code:`helloworld`, and sub-directory :code:`system` (see :numref:`lst:createCaseDir`).

.. code-block:: bash 
    :linenos:
    :caption: Create case directory.
    :name: lst:createCaseDir

    mkdir helloworld
    cd helloworld
    mkdir system

The :code:`controlDict` file is the first and most important file, which is located at :code:`system` directory. 
Create :code:`controlDict` file in :code:`system` directory with script shown in :numref:`lst:helloworld:controlDict`.

.. literalinclude:: /../../../cookbooks/helloworld/system/controlDict
   :language: foam
   :linenos:
   :lines: 8- 
   :emphasize-lines: 9
   :caption: :code:`controlDict`.
   :name: lst:helloworld:controlDict

.. note::
    The key entry :code:`application` has to be set to :code:`HydrothermalSinglePhaseDarcyFoam` which is the solver name.

Step 2: mesh generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this step we create dictionary :code:`blockMeshDict` (just copy :numref:`lst:blockMeshDict`) in :code:`system` to setup geometry of the 2D box.
Then we just run command :code:`blockMesh` to generate mesh (see :numref:`fig:geometry_2Dbox`).
The directory :code:`constant` will be created automatically and the mesh files will be generated 
in :code:`polyMesh` directory.

.. note::

    After step 2, the mesh is basically generated and we can display using :code:`paraFoam` utility default or using ParaView for Docker user.
    The mesh result is shown in :numref:`fig:helloworld:mesh_PV`.

.. figure:: /_figures/helloworld_mesh_PV.png
   :align: center
   :name: fig:helloworld:mesh_PV

   The screenshot of 2D box mesh in ParaView.

Step 3: field data in :code:`0` folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this step, we need to create I/O data files of field :code:`p`, :code:`T` and :code:`permeability` in :code:`0` time directory.
This three files are shown in :code:`lst:helloworld:p`, :code:`lst:helloworld:T` and :code:`lst:helloworld:permeability`, respectively.

.. literalinclude:: /../../../cookbooks/helloworld/0/p
   :language: foam
   :linenos:
   :lines: 8- 
   :caption: Data field :code:`p`.
   :name: lst:helloworld:p

.. literalinclude:: /../../../cookbooks/helloworld/0/T
   :language: foam
   :linenos:
   :lines: 8- 
   :caption: Data field :code:`T`.
   :name: lst:helloworld:T

.. literalinclude:: /../../../cookbooks/helloworld/0/permeability
   :language: foam
   :linenos:
   :lines: 8- 
   :caption: Data field :code:`permeability`.
   :name: lst:helloworld:permeability

.. tip::

    Now we can display the initial filed of :code:`p`, :code:`T` and :code:`permeability` using ParaView. 
    Screenshot of field :code:`T` is shown in :numref:`fig:helloworld:initial_T_PV`.
    In order to view the initial filed, the user have to uncheck the checkbox of :code:`Skip Zero Time` (see red rectangle in the figure)

.. figure:: /_figures/helloworld_initial_T_PV.png
   :align: center
   :name: fig:helloworld:initial_T_PV

   The screenshot of field :code:`T` in ParaView.


Step 4: constant property files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this step we need to copy three constant files 
:code:`g` (shown in :numref:`lst:helloworld:g`), 
:code:`thermophysicalProperties` (:numref:`lst:thermophysicalProperties`) 
and :code:`transportProperties` (:numref:`lst:transportProperties`)
into the :code:`constant` directory.

.. literalinclude:: /../../../cookbooks/helloworld/constant/g
   :language: foam
   :linenos:
   :lines: 8- 
   :caption: Constant property file :code:`g`.
   :name: lst:helloworld:g

.. tip::

    The user can change some propertie values in :code:`transportProperties`, 
    e.g. :code:`porosity`, accroding to a specific modeling problem.

Step 5: setup numerical schemes and solution control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this step we will create numerical schemes and solution control dictionary file 
:code:`fvSchemes` and :code:`fvSolution` in :code:`system` directory.
These two files can be found in :numref:`lst:fvSchemes` and :numref:`lst:fvSolution` in :numref:`sec:system`.

Step 6: run the case
^^^^^^^^^^^^^^^^^^^^^^

Now the simple case setup or pre-processing has been completed. 
The we just run the following simple command (:numref:`lst:helloworld:run`) to run the case.

.. code-block:: bash
    :linenos:
    :name: lst:helloworld:run
    :caption: Command of running the 2D box case.

    blockMesh # mesh generation
    HydrothermalSinglePhaseDarcyFoam # execute the solver application

Step 7: display results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. only:: html 

   We can use :code:`paraFoam` or ParaView (just like step 3) to display results which saved in time directories.
   The time directories name is dependent on key entries :code:`writeInterval`, :code:`purgeWrite` and :code:`timePrecision`.
   The temperature evolution is shown below.


   .. raw:: html

      <video width=100% autoplay loop>
         <source src="https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/video/results_helloworld.mp4" type="video/mp4">
         Your browser does not support HTML video.
      </video>

.. only:: latex

   We can use :code:`paraFoam` or ParaView (just like step 3) to display results which saved in time directories.
   The time directories name is dependent on key entries :code:`writeInterval`, :code:`purgeWrite` and :code:`timePrecision`.
   The temperature is shown in figure :numref:`fig:helloworld:result_T`.


   .. figure:: /_figures/T_helloworld.*
      :align: center
      :name: fig:helloworld:result_T

      Temperature result of the **hello world** model.



.. tip::

   If users want to run a case for a long time, there is an excellent tool named tmux_ ,
   which is a terminal multiplexer. 
   It lets you switch easily between several programs in one terminal, 
   detach them (they keep running in the background) and reattach them to a different terminal.