template <int dim>
  void Simulator<dim>::aspectToFoam ()
  {
    unsigned int max_refinement_level = parameters.initial_global_refinement +
                                        parameters.initial_adaptive_refinement;
    pre_refinement_step = 0;
    if (parameters.resume_computation == true)
      {
        resume_from_snapshot();
        while ((parameters.additional_refinement_times.size() > 0) &&
               (parameters.additional_refinement_times.front () < time+time_step))
          {
            ++max_refinement_level;
            parameters.additional_refinement_times
            .erase (parameters.additional_refinement_times.begin());
          }
      }
    else
      {
        time = parameters.start_time;
        for (unsigned int n=0; n<parameters.initial_global_refinement; ++n)
          {
            for (const auto &cell : triangulation.active_cell_iterators())
              cell->set_refine_flag ();

            mesh_refinement_manager.tag_additional_cells ();
            triangulation.execute_coarsening_and_refinement();
            if (MappingQCache<dim> *map = dynamic_cast<MappingQCache<dim>*>(&(*mapping)))
          #if DEAL_II_VERSION_GTE(9,3,0)
                        map->initialize(MappingQGeneric<dim>(4), triangulation);
          #else
                        map->initialize(triangulation, MappingQGeneric<dim>(4));
          #endif
          }
        setup_dofs();
        global_volume = GridTools::volume (triangulation, *mapping);
      }
    
    // start to convert mesh to OpenFOAM polyMesh
    // std::ofstream out("mesh.vtu");
    // GridOut       grid_out;
    // grid_out.write_vtu(triangulation, out);
    Triangulation2PolyMesh(triangulation, dof_handler, finite_element, solution, introspection, mesh_deformation->mesh_deformation_dof_handler, mesh_deformation->mesh_displacements,"OpenFOAM",parameters.mesh_deformation_enabled);
    std::cout<<"finished!\n";
  }