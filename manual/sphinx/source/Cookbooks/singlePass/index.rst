.. include:: /include.rst_


.. _sec:cookbooks_singlepass:

Single pass model
===================

.. _sec_cookbook_singlepass_2D:

Two-dimensional single pass model
-------------------------------------

All the input files can be found in |singlepass| directory.

One- and two-limb single-pass models are usually used to determine vent field characteristics 
such as mass flow rate :math:`Q`, 
bulk permeability in the discharge zone :math:`k_d`, 
thickness of the conductive boundary layer at the base of the system :math:`d`, 
magma replenishment rate, 
and residence time in the discharge zone :cite:`lowell2013`.

One-limb classical single pass model 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A schematic of the one- and two-limb single-pass model are shown in :numref:`fig:singlepass_Lowell`.

.. figure:: /_figures/singlepass_Lowell.*
    :align: center
    :name: fig:singlepass_Lowell

    Schematic of the one-limb (A) and two-limb (B) single-pass model (reproduced from :cite:`lowell2013`).

Here we present the one-limb single pass mode simulation using |foam|, 
the model geometry, mesh and boundary conditions are shown in :numref:`fig:singlepass:model`.


.. figure:: /_figures/model_singlepass.*
    :align: center
    :name: fig:singlepass:model

    Model geometry, mesh and boundary conditions of the 2D single pass model.

.. only:: html

    
    The model setup is similar to :cite:`lowell2007`.
    The temperature evolution and streamlines of the :ref:`sec_cookbook_singlepass_2D` are shown below.

    .. tab:: Temperature evolution

        .. raw:: html

            <video width=100% autoplay loop>
                <source src="https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/video/results_singlepass.mp4" type="video/mp4">
                Your browser does not support HTML video.
            </video>

    .. tab:: Streamlines and velocity arrows

        This is a interactive vtk scense.

        .. raw:: html
            
            <iframe src="../../_static/vtk_js/index.html?fileURL=https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/vtk_js/singlepass_result.vtkjs" width="100%" height="500px"></iframe>

.. only:: latex

    The model setup is similar to :cite:`lowell2007`.
    The temperature evolution and streamlines of the :ref:`sec_cookbook_singlepass_2D` are in :numref:`fig:singlepass:result_T`.

    .. figure:: /_figures/T_singlepass.*
        :align: center
        :name: fig:singlepass:result_T

        Temperature result of the :ref:`sec_cookbook_singlepass_2D`.

If we consider the recharge zone on the right side in single pass model shown in :numref:`fig:singlepass:model`,
the hydrothermal circulation pattern would be different, 
a schematic of the full single pass model is shown in :numref:`fig:singlepass_Lowell2014:model`.

.. figure:: /_figures/singlepass_Lowell2014.*
    :align: center
    :name: fig:singlepass_Lowell2014:model

    Schematic of the full single-pass model (reproduced from :cite:`lowell2014`).

Here we present the full single pass mode simulation using |foam|, 
the model geometry, mesh and boundary conditions are shown in :numref:`fig:singlepass2:model`.
  

.. figure:: /_figures/model_singlepass2.*
    :align: center
    :name: fig:singlepass2:model

    Model geometry, mesh and boundary conditions of the improved 2D single pass model.

.. only:: html

    The temperature evolution and streamlines of the full :ref:`sec_cookbook_singlepass_2D` are shown below.

    .. tab:: Temperature evolution

        .. raw:: html

            <video width=100% autoplay loop>
                <source src="https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/video/results_singlepass2.mp4" type="video/mp4">
                Your browser does not support HTML video.
            </video>

    .. tab:: Streamlines and velocity arrows

        This is a interactive vtk scense.

        .. raw:: html
            
            <iframe src="../../_static/vtk_js/index.html?fileURL=https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/vtk_js/singlepass2_result.vtkjs" width="100%" height="500px"></iframe>

.. only:: latex

    The temperature evolution and streamlines of the full :ref:`sec_cookbook_singlepass_2D` are in :numref:`fig:singlepass:result_T`.

    .. figure:: /_figures/T_singlepass2.*
        :align: center
        :name: fig:singlepass2:result_T

        Temperature result of the :ref:`sec_cookbook_singlepass_2D`.

Two-limb single pass model 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All the input files can be found in |singlepass_twolimb| directory.
The model geometry, mesh and boundary conditions are shown in :numref:`fig:singlepass_twolimb:model`

.. figure:: /_figures/model_singlepass_twolimb.*
    :align: center
    :name: fig:singlepass_twolimb:model

    Model geometry, mesh and boundary conditions of the two-dimensional two-limb single pass model. 

.. only:: html

    The temperature evolution and streamlines of the two-limb single pass model are shown below.

    .. tab:: Temperature evolution

        .. raw:: html

            <video width=100% autoplay loop>
                <source src="https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/video/results_singlepass_twolimb.mp4" type="video/mp4">
                Your browser does not support HTML video.
            </video>

    .. tab:: Streamlines and velocity arrows

        This is a interactive vtk scense.

        .. raw:: html
            
            <iframe src="../../_static/vtk_js/index.html?fileURL=https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/vtk_js/singlepass_twolimb_result.vtkjs" width="100%" height="500px"></iframe>

.. only:: latex

    The temperature evolution and streamlines of the two-limb single pass model are in :numref:`fig:singlepass_twolimb:result_T`.

    .. figure:: /_figures/T_singlepass_twolimb.*
        :align: center
        :name: fig:singlepass_twolimb:result_T

        Temperature result of the :ref:`sec_cookbook_singlepass_2D`.