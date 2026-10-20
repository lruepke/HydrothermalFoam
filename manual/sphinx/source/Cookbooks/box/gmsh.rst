.. include:: /include.rst_
 
.. _cookbook_gmsh:

Gmsh 
-------  

All the input files can be found in |gmsh| directory.

This example is based on :ref:`cookbook_helloworld`, 
the only difference is the mesh generation.
We use Gmsh_ to generate an unstructured triangular mesh.
The gmsh script :download:`box.geo <https://gitlab.com/gmdpapers/hydrothermalfoam/-/tree/master/cookbooks/gmsh/gmsh/box.geo>` is shown in :numref:`lst:gmsh:box.geo`.

.. literalinclude:: /../../../cookbooks/gmsh/gmsh/box.geo
   :language: gmsh   
   :linenos:
   :lines: 1-38
   :emphasize-lines: 7, 28, 23-24
   :caption: Gmsh geometry script of the :ref:`cookbook_gmsh` model.
   :name: lst:gmsh:box.geo

.. tip::

    The Gmsh_ can generate regular mesh as well, see lines 23-24 in :numref:`lst:gmsh:box.geo`.

The model geometry, boundary conditions and mesh structure are shown in :numref:`fig:gmsh`.

.. figure:: /_figures/model_gmsh.*
   :align: center
   :name: fig:gmsh

   The geometry, boundary conditions and mesh structure of the :ref:`cookbook_gmsh` model.

.. only:: html

   The temperature evolution is shown below.

   .. raw:: html

      <video width=100% autoplay loop>
         <source src="https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/video/results_gmsh.mp4" type="video/mp4">
         Your browser does not support HTML video.
      </video>


.. only:: latex

   The temperature result is shown in :numref:`fig:gmsh:result_T`

   .. figure:: /_figures/T_gmsh.*
      :align: center
      :name: fig:gmsh:result_T

      Temperature result of the :ref:`cookbook_gmsh` model.