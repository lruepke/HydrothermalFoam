

.. include:: /include.rst_

.. _sec:convection_3Dbox:

3D box
----------

All the input files can be found in |3Dbox| directory.

This example is based on models in :numref:`cookbook_nonUniformFixedValueBC` and :numref:`cookbook_gmsh`.
We just to make the following three changes to make a 3D box model,

#. For mesh generation, we just need to change :code:`zmax=xmax;` and change the extrude layers to a number greater than 1, e.g. 40, see line 7 and line 28 in :numref:`lst:gmsh:box.geo`.

#. For boundary conditions, we just need to change :code:`type` of :code:`frontAndBack` boundary to be consistent with the :code:`left` and :code:`right` boundary, rather than :code:`empty`. And then change :code:`bottom` boundary condition of :code:`T` similar to example :numref:`cookbook_nonUniformFixedValueBC`, see :numref:`lst:3Dbox:BC_T`.

#. Unlike 2D model, we don't need to set :code:`frontAndBack` to empty patch in :code:`polyMesh/boundary` file. See :numref:`sec:convertGmsh` for empty boundary of 2D model.

.. code-block:: foam
    :linenos:
    :name: lst:3Dbox:BC_T
    :caption: Bottom boundary condition of :code:`T` of the 3D box model.
    :emphasize-lines: 8, 11, 14

    bottom
    {
        type            codedFixedValue;
        value           uniform 873.15; //placeholder
        name            gaussShapeT;
        code            #{
                            scalarField x(this->patch().Cf().component(0)); 
                            scalarField z(this->patch().Cf().component(2)); 
                            double wGauss=200;
                            double x0=1000;
                            double z0=1000;
                            double Tmin=573;
                            double Tmax=873.15;
                            scalarField T(Tmin+(Tmax-Tmin)*exp(-((x-x0)*(x-x0)+(z-z0)*(z-z0))/(2*wGauss*wGauss)));
                            operator==(T);
                        #};
    }

.. only:: html

    The mesh and bottom boundary condition of temperature are shown in the following static figure and interactive vtk scene.


    .. tab:: Mesh

        .. figure:: /_figures/3Dbox_mesh_gmsh.png
            :align: center

            The screenshot of mesh of 3D box model.

    .. tab:: BC

        .. figure:: /_figures/model_3Dbox.jpg
            :align: center

            The bottom boundary condition of temperature of the 3D box model.

    .. tab:: Interactive

        Mesh and bottom boundary condition of temperature.

        .. raw:: html
            
            <iframe src="../../_static/vtk_js/index.html?fileURL=https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/vtk_js/3Dbox_mesh_bcT.vtkjs" width="100%" height="500px"></iframe>

.. only:: latex

    The mesh is shown in :numref:`fig:3Dbox:mesh` and the bottom boundary condition of temperature is shown in :numref:`fig:3Dbox:bcT`.

    .. figure:: /_figures/3Dbox_mesh_gmsh.png
        :align: center
        :name: fig:3Dbox:mesh

        The screenshot of mesh of 3D box model.
    
    .. figure:: /_figures/model_3Dbox.pdf
        :align: center
        :name: fig:3Dbox:bcT

        The bottom boundary condition of temperature of the 3D box model.

    
.. only:: html

    The isothermal surface of 300 |degC| , flow arrows and stream lines are shown below.

    .. raw:: html
                
        <iframe src="../../_static/vtk_js/index.html?fileURL=https://raw.githubusercontent.com/zguoch/HydrothermalFoam_static/master/vtk_js/3Dbox_result.vtkjs" width="100%" height="500px"></iframe>

.. only:: latex

    The isothermal surface of 300 |degC| , flow arrows and stream lines are shown below.

    .. figure:: /_figures/3Dbox_result.png
        :align: center
        :name: fig:3Dbox:result

        The isothermal surface of 300 |degC| = 573.15 K, flow arrows and stream lines of the 3D box simulation at 265 year. The unit of temperature in this figure is K.