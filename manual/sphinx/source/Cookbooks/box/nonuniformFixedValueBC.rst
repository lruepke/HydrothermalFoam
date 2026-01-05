.. include:: /include.rst_

.. _cookbook_nonUniformFixedValueBC:

Nonuniform fixed temperature BC
---------------------------------

All the input files can be found in |nonUniformFixedValueBC| directory.

This exmple, based on :ref:`cookbook_helloworld`, presents how to set a nonuniform fixed boundary condition by using :code:`codedFixedValue` BC type (see :numref:`lst:nonUniformFixedValueBC:T`)

.. literalinclude:: /../../../cookbooks/nonUniformFixedValueBC/0/T
   :language: foam
   :linenos:
   :lines: 37-51
   :emphasize-lines: 7, 13
   :caption: Example of nonuniform boundary condition: :code:`codedFixedValue`.
   :name: lst:nonUniformFixedValueBC:T

The model geometry and boundary conditions are shown in :numref:`fig:nonUniformFixedValueBC`.

.. figure:: /_figures/model_nonUniformFixedValueBC.*
   :align: center
   :name: fig:nonUniformFixedValueBC
 
   The geometry and boundary conditions of the :ref:`cookbook_nonUniformFixedValueBC` model.

.. only:: html

   The temperature evolution is shown below.

   .. raw:: html

      <video width=100% autoplay loop>
         <source src="https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/video/results_nonuniformFixedValueBC.mp4" type="video/mp4">
         Your browser does not support HTML video.
      </video>


.. only:: latex 

   The temperature result is shown in :numref:`fig:nonUniformFixedValueBC:result_T`

   .. figure:: /_figures/T_nonUniformFixedValueBC.*
      :align: center
      :name: fig:nonUniformFixedValueBC:result_T

      Temperature result of the :ref:`cookbook_nonUniformFixedValueBC` model.
