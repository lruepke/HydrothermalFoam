
.. include:: /include.rst_

.. _sec:convection_3Dbox_par:

Parallel computing
----------------------

All the input files can be found in |3Dbox_par| directory.

Parallel computing is one of features of OpenFOAM, and the |foam| fully inherits this feature.
There are two steps to run a case in Parallel,

#. Add :code:`decomposeParDict` dictionary file into :code:`system` directory (see :numref:`lst:decomposeParDict`).

#. Decomposition of mesh and initial field data. 

#. Replace :code:`runApplication $application` with :code:`runParallel $application`

#. Reconstructing mesh and data.

The last three steps can be assembled in :code:`run.sh` which is highlighed in :numref:`lst:3Dbox_par:run`

.. literalinclude:: /../../../cookbooks/3Dbox_par/run.sh
   :language: bash
   :linenos:
   :lines: 1-
   :emphasize-lines: 16-18
   :caption: Command set of running a case in parallel.
   :name: lst:3Dbox_par:run

The mesh will be decomposed into multiple connected regions, 
the decomposed region number is defined in :code:`decomposeParDict` file.
The mesh of this example, which is based on 3D box model in  :numref:`sec:convection_3Dbox`, 
is decomposed into 4 regions by using :code:`decomposePar` command in step 2.


.. only:: html

    The decomposed mesh of the 3D box model is shown in the following static figure and interactive vtk scene.

    .. tab:: Mesh

        .. figure:: /_figures/3Dbox_par_mesh.png
            :align: center

            The decomposed mesh of the 3D box.

    .. tab:: Interactive

        The decomposed mesh of the 3D box.

        .. raw:: html
            
            <iframe src="../../_static/vtk_js/index.html?fileURL=https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/vtk_js/3Dbox_par_mesh.vtkjs" width="100%" height="500px"></iframe>

.. only:: latex

    The decomposed mesh of the 3D box model is shown in :numref:`fig:3Dbox_par:mesh`.

    .. figure:: /_figures/3Dbox_par_mesh.png
        :align: center
        :name: fig:3dbox_par:mesh

        The decomposed mesh of the 3D box.
