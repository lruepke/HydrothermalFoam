.. _sec:cookbooks_timePerm:

.. include:: /include.rst_

.. _cookbook_timeDependentPerm:

Time-dependent permeability
-------------------------------

All the input files can be found in |timeDependentPerm| directory.

The change of permeability over time, e.g. due to mineral precipitation,
is an important process real hydrothermal systems.
This exmple, based on :ref:`cookbook_helloworld`, 
presents how to set time-dependent permeability at run time in |foam| tools.
This can be reached using :code:`function` sub-dictionary in :code:`controlDict` file (see :numref:`lst:timeDependentPerm:controlDict`).


.. literalinclude:: /../../../cookbooks/timeDependentPerm/system/controlDict
   :language: foam
   :linenos:
   :lines: 37-73
   :emphasize-lines: 14, 16, 26, 28
   :caption: Change permeability at run time: :code:`controlDict`.
   :name: lst:timeDependentPerm:controlDict

The model geometry and boundary conditions are shown in :numref:`fig:timeDependentPerm`, 
the permeability in shallow region (depth < 2.4 km) will be increase after 500 years (the inset curve).

.. figure:: /_figures/model_timeDependentPerm.*
   :align: center
   :name: fig:timeDependentPerm

   The geometry, BCs and permeability of the :ref:`cookbook_timeDependentPerm` model.

.. only:: html

   The temperature evolution is shown below.

   .. raw:: html

      <video width=100% autoplay loop>
         <source src="https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/video/results_timeDependentPerm.mp4" type="video/mp4">
         Your browser does not support HTML video.
      </video>

.. only:: latex 

   The temperature and permeability results are shown in :numref:`fig:timeDependentPerm:result_T`.

   .. figure:: /_figures/T_timeDependentPerm.*
      :align: center
      :name: fig:timeDependentPerm:result_T

      Temperature and permeability result of the :ref:`cookbook_timeDependentPerm` model.